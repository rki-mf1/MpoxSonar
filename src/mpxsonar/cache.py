#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Stephan Fuchs (Robert Koch Institute, MF1, fuchss@rki.de)

import base64
from collections import defaultdict
import hashlib
import logging
import os
import pickle
import pprint
import re
import shutil
import sys
import traceback

from mpire import WorkerPool
import pandas as pd
from tqdm import tqdm

from .align import sonarAligner
from .config import TMP_CACHE
from .dbm import sonarDBManager
from .utils import harmonize
from .utils import hash
from .utils import open_file

# from .basics import sonarBasics

pp = pprint.PrettyPrinter(indent=4)


class sonarCache:
    """ """

    def __init__(
        self,
        db=None,
        outdir=None,
        refacc=None,
        logfile=None,
        allow_updates=True,
        ignore_errors=False,
        temp=False,
        debug=False,
        disable_progress=False,
    ):
        self.db = db
        self.allow_updates = allow_updates
        self.debug = debug
        self.refacc = refacc
        self.temp = temp
        self.ignore_errors = ignore_errors
        self.disable_progress = disable_progress

        with sonarDBManager(self.db, debug=self.debug) as dbm:
            self.refmols = dbm.get_molecule_data(
                "`molecule.accession`",
                "`molecule.id`",
                "`molecule.standard`",
                "`translation.id`",
                reference_accession=self.refacc,
            )
            if not self.refmols:
                logging.info(f"Cannot find reference: {self.refacc}")
                sys.exit()
            if self.debug:
                logging.info(f"Init refmols: {self.refmols}")
            """
            self.default_refmol_acc = [
                x for x in self.refmols if self.refmols[x]["molecule.standard"] == 1
            ][0]
            self.default_refmol_id = [
                x for x in self.refmols if self.refmols[x]["molecule.id"] == 1
            ][0]
            self.sources = {
                x["molecule.accession"]: dbm.get_source(x["molecule.id"])
                for x in self.refmols.values()
            }
            """
            self.default_refmol_acc = [
                x for x in self.refmols if self.refmols[x]["molecule.standard"] == 1
            ][0]

            self.default_refmol_id = [
                self.refmols[x]["molecule.id"] for x in self.refmols
            ][0]

            self.sources = {
                x["molecule.accession"]: dbm.get_source(x["molecule.id"])
                for x in self.refmols.values()
            }
            self.properties = dbm.properties

        self._propregex = re.compile(
            r"\[(" + "|".join(self.properties.keys()) + r")=([^\[\]=]+)\]"
        )
        self._molregex = re.compile(r"\[molecule=([^\[\]=]+)\]")

        self.basedir = TMP_CACHE if not outdir else os.path.abspath(outdir)

        if not os.path.exists(self.basedir):
            os.makedirs(self.basedir)

        self.logfile = (
            open(os.path.join(self.basedir, logfile), "a+") if logfile else None
        )
        self.smk_config = os.path.join(self.basedir, "config.yaml")
        self.sample_dir = os.path.join(self.basedir, "samples")
        self.seq_dir = os.path.join(self.basedir, "seq")
        self.algn_dir = os.path.join(self.basedir, "algn")
        self.var_dir = os.path.join(self.basedir, "var")
        self.ref_dir = os.path.join(self.basedir, "ref")
        self.error_dir = os.path.join(self.basedir, "error")
        os.makedirs(self.basedir, exist_ok=True)
        os.makedirs(self.seq_dir, exist_ok=True)
        os.makedirs(self.ref_dir, exist_ok=True)
        # os.makedirs(self.algn_dir, exist_ok=True)
        os.makedirs(self.var_dir, exist_ok=True)
        os.makedirs(self.sample_dir, exist_ok=True)
        os.makedirs(self.error_dir, exist_ok=True)

        self._samplefiles = set()
        self._samplefiles_to_profile = set()
        self._refs = set()
        self._lifts = set()
        self._tt = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if os.path.isdir(self.basedir) and self.temp:
            shutil.rmtree(self.basedir)
        if self.logfile:
            self.logfile.close()

    @staticmethod
    def slugify(string):
        return (
            base64.urlsafe_b64encode(string.encode("UTF-8")).decode("UTF-8").rstrip("=")
        )

    # Do we need this function?
    # @staticmethod
    # def deslugify(string):
    #    while len(string) % 3 != 0:
    #        string += "="
    #    return base64.urlsafe_b64decode(string).decode("utf-8")

    def log(self, msg, die=False, errtype="error"):
        if self.logfile:
            self.logfile.write(msg + "\n")
        elif not die:
            sys.stderr.write(msg + "\n")
        else:
            exit(errtype + ": " + msg)

    @staticmethod
    def write_pickle(fname, data):
        with open(fname, "wb") as handle:
            pickle.dump(data, handle)

    @staticmethod
    def read_pickle(fname):
        with open(fname, "rb") as handle:
            return pickle.load(handle, encoding="bytes")

    # Do we need this function?
    # @staticmethod
    # def pickle_collision(fname, data):
    #     if os.path.isfile(fname) and load_pickle(fname) != data:
    #        return True
    #    return False

    @staticmethod
    def file_collision(fname, data):
        with open(fname, "r") as handle:
            if handle.read() != data:
                return True
        return False

    # Do we need this function?
    # def sample_collision(self, key, datadict):
    #    if sonarCache.read_pickle(key) != datadict:
    #        return True
    #    return False

    # Do we need this function?
    # def write_smk_config(self):
    #    data = {
    #        "debug": self.debug,
    #        "sample_dir": self.sample_dir,
    #        "seq_dir": self.seq_dir,
    #        "algn_dir": self.algn_dir,
    #        "var_dir": self.var_dir,
    #    }

    #    with open(self.smk_config, "w") as handle:
    #        yaml.dump(data, handle)

    def get_seq_fname(self, seqhash):
        fn = self.slugify(seqhash)
        return os.path.join(self.seq_dir, fn[:2], fn + ".seq")

    def get_ref_fname(self, refid):
        return os.path.join(self.ref_dir, str(refid) + ".seq")

    def get_lift_fname(self, refid):
        return os.path.join(self.ref_dir, str(refid) + ".lift")

    def get_tt_fname(self, refid):
        return os.path.join(self.ref_dir, str(refid) + ".tt")

    def get_algn_fname(self, seqhash):
        fn = self.slugify(seqhash)
        return os.path.join(self.algn_dir, fn[:2], fn + ".algn")

    def get_var_fname(self, seqhash):
        fn = self.slugify(seqhash)
        return os.path.join(self.var_dir, fn[:2], fn + ".var")

    def get_sample_fname(self, sample_name):
        fn = self.slugify(hashlib.sha1(sample_name.encode("utf-8")).hexdigest())
        return os.path.join(self.sample_dir, fn[:2], fn + ".sample")

    def cache_sample(
        self,
        name,
        sampleid,
        seqhash,
        header,
        refmol,
        refmolid,
        sourceid,
        translation_id,
        algnid,
        seqfile,
        reffile,
        ttfile,
        algnfile,
        varfile,
        liftfile,
        properties,
    ):
        """
        The function takes in a bunch of arguments and returns a filename.
        :return: A list of dictionaries. Each dictionary contains the information for a single sample.
        """

        data = {
            "name": name,
            "sampleid": sampleid,
            "refmol": refmol,
            "refmolid": refmolid,
            "sourceid": sourceid,
            "translationid": translation_id,
            "algnid": algnid,
            "header": header,
            "seqhash": seqhash,
            "seq_file": seqfile,
            "ref_file": reffile,
            "tt_file": ttfile,
            "algn_file": algnfile,
            "var_file": varfile,
            "lift_file": liftfile,
            "properties": properties,
        }
        fname = self.get_sample_fname(name)  # full path

        self.log("Get:" + fname)

        try:
            self.write_pickle(fname, data)
        except OSError:
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            self.write_pickle(fname, data)

        self._samplefiles.add(fname)
        if algnid is None:
            self._samplefiles_to_profile.add(fname)
        return fname

    def iter_samples(self):
        for fname in self._samplefiles:
            yield self.read_pickle(fname)

    def cache_sequence(self, seqhash, sequence):
        fname = self.get_seq_fname(seqhash)
        if os.path.isfile(fname):
            if self.file_collision(fname, sequence):
                sys.exit(
                    "seqhash collision: sequences differ for seqhash " + seqhash + "."
                )
        else:
            try:
                with open(fname, "w") as handle:
                    handle.write(sequence)
            except OSError:
                os.makedirs(os.path.dirname(fname), exist_ok=True)
                with open(fname, "w") as handle:
                    handle.write(sequence)
        return fname

    def cache_reference(self, refid, sequence):
        fname = self.get_ref_fname(refid)
        if refid not in self._refs:
            with open(fname, "w") as handle:
                handle.write(sequence)
            self._refs.add(refid)
        return fname

    def cache_translation_table(self, translation_id, dbm):
        """
        If the translation table
        is not in the cache, it is retrieved from the database and written to a file

        :param translation_id: The id of the translation table
        :param dbm: the database manager
        :return: A file name.
        """
        fname = self.get_tt_fname(translation_id)  # write under /cache/ref/
        if translation_id not in self._tt:
            self.write_pickle(fname, dbm.get_translation_dict(translation_id))
            self._tt.add(translation_id)
        return fname

    def cache_lift(self, refid, refmol_acc, sequence):
        """
                The function takes in a reference id, a reference molecule accession number,
                and a reference sequence. It then checks to see if the reference molecule accession number is in the set of molecules that
                have been cached. If it is not, it iterates through all of the coding sequences for that molecule and creates a
                dataframe for each one.
        .
                It then saves the dataframe to a pickle file and adds the reference molecule accession number to
                the set of molecules that have been cached.
                It then returns the name of the pickle file
        """
        fname = self.get_lift_fname(refid)
        rows = []
        if refmol_acc not in self._lifts:
            cols = [
                "elemid",
                "nucPos1",
                "nucPos2",
                "nucPos3",
                "ref1",
                "ref2",
                "ref3",
                "alt1",
                "alt2",
                "alt3",
                "symbol",
                "aaPos",
                "aa",
            ]
            # if there is no cds, the lift file will not be generated
            for cds in self.iter_cds(refmol_acc):
                elemid = cds["id"]
                symbol = cds["symbol"]
                seq = cds["sequence"] + "*"
                codon = 0
                i = 0
                coords = []
                for rng in cds["ranges"]:
                    coords.extend(list(rng))
                while len(coords) % 3 != 0:
                    coords.append("")
                coords_len = len(coords)
                while len(seq) < coords_len / 3:
                    seq += "-"
                while len(sequence) < coords_len:
                    sequence += "-"
                for i, coord in enumerate(
                    [coords[x : x + 3] for x in range(0, len(coords), 3)]
                ):
                    codon = [sequence[coord[0]], sequence[coord[1]], sequence[coord[2]]]
                    rows.append(
                        [elemid] + coord + codon + codon + [symbol, i, seq[i].strip()]
                    )
            df = pd.DataFrame.from_records(rows, columns=cols, coerce_float=False)
            df = df.reindex(df.columns.tolist(), axis=1)
            df.to_pickle(fname)
            if self.debug:
                df.to_csv(fname + ".csv")
            self._lifts.add(refmol_acc)

        return fname

    def process_fasta_entry(self, header, seq):
        sample_id = header.replace("\t", " ").replace("|", " ").split(" ")[0]
        refmol = self.get_refmol(header)
        if not refmol:
            sys.exit(
                "input error: "
                + sample_id
                + " refers to an unknown reference molecule ("
                + self._molregex.search(header)
                + ")."
            )
        seq = harmonize(seq)
        seqhash = hash(seq)
        refmolid = self.refmols[refmol]["molecule.id"]
        return {
            "name": sample_id,
            "header": header,
            "seqhash": seqhash,
            "sequence": seq,
            "refmol": refmol,
            "refmolid": refmolid,
            "translation_id": self.refmols[refmol]["translation.id"],
            "properties": self.get_properties(header),
        }

    def iter_fasta(self, *fnames):
        """
        This function iterates over the fasta files and returns a dictionary for each record
        """
        for fname in fnames:
            with open_file(fname, compressed="auto") as handle, tqdm(
                desc="processing " + fname + "...",
                total=os.path.getsize(fname),
                unit="bytes",
                unit_scale=True,
                bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
                disable=self.disable_progress,
            ) as pbar:
                seq = []
                header = None
                for line in handle:
                    pbar.update(len(line))
                    line = line.strip()
                    if line.startswith(">"):
                        if seq:
                            yield self.process_fasta_entry(header, "".join(seq))
                            seq = []
                        header = line[1:]
                    else:
                        seq.append(line)
                if seq:
                    yield self.process_fasta_entry(header, "".join(seq))

    def get_refmol(self, fasta_header):
        """

        return:
            None: if cannot find mol_id from the header
        """
        mol = self._molregex.search(fasta_header)
        if not mol:
            try:
                print(f"Using refmol_acc: {self.refmols[mol]['accession']}")
                return self.refmols[mol]["accession"]
            except Exception:
                None
        if self.debug:
            logging.INFO(
                f"Using default (given) reference mol accession: {self.default_refmol_acc}"
            )
        return self.default_refmol_acc

    def get_refseq(self, refmol_acc):
        try:
            return self.sources[refmol_acc]["sequence"]
        except Exception:
            return None

    def iter_cds(self, refmol_acc):
        cds = {}
        prev_elem = None
        with sonarDBManager(self.db, debug=self.debug) as dbm:
            for row in dbm.get_annotation(
                reference_accession=refmol_acc,
                molecule_accession=refmol_acc,
                element_type="cds",
            ):
                if prev_elem is None:
                    prev_elem = row["element.id"]
                elif row["element.id"] != prev_elem:
                    yield cds
                    cds = {}
                    prev_elem = row["element.id"]
                if cds == {}:
                    cds = {
                        "id": row["element.id"],
                        "accession": row["element.accession"],
                        "symbol": row["element.symbol"],
                        "sequence": row["element.sequence"],
                        "ranges": [
                            range(
                                row["elempart.start"],
                                row["elempart.end"],
                                row["elempart.strand"],
                            )
                        ],
                    }
                else:
                    cds["ranges"].append(
                        range(
                            row["elempart.start"],
                            row["elempart.end"],
                            row["elempart.strand"],
                        )
                    )
        if cds:
            yield cds

    def get_refseq_id(self, refmol_acc):
        try:
            return self.sources[refmol_acc]["id"]
        except Exception:
            return None

    def get_refhash(self, refmol_acc):
        try:
            if "seqhash" not in self.sources[refmol_acc]:
                self.sources[refmol_acc]["seqhash"] = hash(
                    self.sources[refmol_acc]["sequence"]
                )
            return self.sources[refmol_acc]["seqhash"]
        except Exception:
            return None

    def get_properties(self, fasta_header):
        return {x.group(1): x.group(2) for x in self._propregex.finditer(fasta_header)}

    def add_fasta(self, *fnames, propdict=defaultdict(dict)):  # noqa: C901
        default_properties = {
            x: self.properties[x]["standard"] for x in self.properties
        }
        failed_list = []
        with sonarDBManager(self.db, debug=self.debug) as dbm:
            for fname in fnames:
                for data in self.iter_fasta(fname):
                    # EDIT: we currently lock the filtering part. print(data)
                    # check sequence lenght
                    # if not check_seq_compact(
                    #    self.get_refseq(data["refmol"]), data["sequence"]
                    # ):
                    #    failed_list.append((data["name"], len(data["sequence"])))
                    # log fail samples
                    #    continue

                    # check sample
                    data["sampleid"], seqhash = dbm.get_sample_data(data["name"])
                    data["sourceid"] = dbm.get_source(data["refmolid"])["id"]

                    # check properties
                    if data["sampleid"] is None:
                        props = default_properties
                        for k, v in data["properties"].items():
                            props[k] = v
                        for k, v in propdict[data["sampleid"]].items():
                            props[k] = v
                        data["properties"] = props
                    elif not self.allow_updates:
                        continue
                    else:
                        for k, v in propdict[data["sampleid"]].items():
                            data["properties"][k] = v

                    # check reference
                    # print("refmol", data)
                    # CHANGED IN MPXsonar: use ref acc
                    # refseq_id = self.get_refseq_id(data["refmol"]) from old covsonar
                    refseq_id = data["refmol"]

                    self.write_checkref_log(data, refseq_id)

                    # check alignment
                    data["algnid"] = dbm.get_alignment_id(data["seqhash"], refseq_id)
                    data = self.assign_data(data, seqhash, refseq_id, dbm)
                    del data["sequence"]
                    self.cache_sample(**data)
        if failed_list:
            self.log(
                "Sample will not be processed due to violate max/min seq lenght rule (+-3%):"
                + str(failed_list),
            )
            logging.warn("Fail max/min seq lenght rule:" + str(failed_list))

    def write_checkref_log(self, data, refseq_id):
        """this function linked to the add_fasta"""
        if not refseq_id:
            if not self.ignore_errors:
                self.log(
                    "fasta header refers to an unknown refrence ("
                    + data["header"]
                    + ")",
                    True,
                    "input error",
                )
            else:
                self.log(
                    "skipping "
                    + data["name"]
                    + " referring to an unknown reference ("
                    + data["header"]
                    + ")"
                )

    def assign_data(self, data, seqhash, refseq_id, dbm):
        """this function linked to the add_fasta
        refseq_id is ID from element table.
        ref_acc is accession in reference table.

        """
        if data["algnid"] is None:
            data["seqfile"] = self.cache_sequence(data["seqhash"], data["sequence"])
            # TODO: get ref accession number and put into cache_lift
            # to fix recreate cache directory *(optional task)
            data["reffile"] = self.cache_reference(
                refseq_id, self.get_refseq(data["refmol"])
            )

            data["ttfile"] = self.cache_translation_table(data["translation_id"], dbm)
            data["liftfile"] = self.cache_lift(
                refseq_id, data["refmol"], self.get_refseq(data["refmol"])
            )
            data["algnfile"] = self.get_algn_fname(
                data["seqhash"] + "@" + self.get_refhash(data["refmol"])
            )
            data["varfile"] = self.get_var_fname(
                data["seqhash"] + "@" + self.get_refhash(data["refmol"])
            )
        else:
            if data["seqhash"] != seqhash:
                data["seqfile"] = self.cache_sequence(data["seqhash"], data["sequence"])
            else:
                data["seqhash"] = None
                data["seqfile"] = None

            data["reffile"] = None
            data["ttfile"] = None
            data["liftfile"] = None
            data["algnfile"] = None
            data["varfile"] = None
        return data

    def import_cached_samples(self, threads):  # noqa: C901
        list_fail_samples = []
        refseqs = {}
        count_sample = 0
        with sonarDBManager(self.db, readonly=False, debug=self.debug) as dbm:
            for sample_data in tqdm(
                self.iter_samples(),
                total=len(self._samplefiles),
                desc="importing samples...",
                unit="samples",
                bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
                disable=self.disable_progress,
            ):
                # print("\n")
                # print("-----####------ sample_data -----####------")
                # print(sample_data)

                try:
                    # nucleotide level import
                    if not sample_data["seqhash"] is None:
                        dbm.insert_sample(sample_data["name"], sample_data["seqhash"])
                        # self.log("sample_data:" + str(sample_data))
                        # sample_data["refmolid"]
                        # print("-----####------ insert_alignment -----####------")
                        # print(sample_data["seqhash"], sample_data["sourceid"])
                        algnid = dbm.insert_alignment(
                            sample_data["seqhash"], sample_data["sourceid"]
                        )
                        # self.log("Get algnid:" + algnid)
                    if not sample_data["var_file"] is None:
                        with open(sample_data["var_file"], "r") as handle:
                            for line in handle:
                                if line == "//":
                                    break
                                vardat = line.strip("\r\n").split("\t")
                                dbm.insert_variant(
                                    algnid,
                                    vardat[4],
                                    vardat[0],
                                    vardat[3],
                                    vardat[1],
                                    vardat[2],
                                    vardat[5],
                                )
                            if line != "//":
                                sys.exit(
                                    "cache error: corrupted file ("
                                    + sample_data["var_file"]
                                    + ")"
                                )
                    # paranoia test
                    if not sample_data["seqhash"] is None:
                        paranoid_dict = self.paranoid_check(refseqs, sample_data, dbm)
                        if paranoid_dict:
                            list_fail_samples.append(paranoid_dict)
                        count_sample = count_sample + 1
                except Exception as e:
                    logging.error("\n------- Fatal Error ---------")
                    print(traceback.format_exc())
                    print("\nDebugging Information:")
                    print(e)
                    print("\n During insert:")
                    pp.pprint(sample_data)
                    sys.exit("Unknown import error")
        if list_fail_samples:
            logging.info(
                f"Start paranoid alignment on {len(list_fail_samples)} sample."
            )
            self.paranoid_align_multi(list_fail_samples, threads)
        count_sample = count_sample - len(list_fail_samples)
        logging.info("Total sample insert: " + str(count_sample))

    def _align(self, output_paranoid, qryfile, reffile, sample_name):
        # print(output_paranoid, qryfile, reffile, sample_name)

        if not os.path.exists(output_paranoid):
            aligner = sonarAligner(cache_outdir=self.basedir)

            qry, ref = aligner.align(qryfile, reffile)
            with open(output_paranoid, "w+") as handle:
                handle.write(
                    ">original_"
                    + sample_name
                    + "\n"
                    + ref
                    + "\n>restored_"
                    + sample_name
                    + "\n"
                    + qry
                    + "\n"
                )
        logging.warn(f"See {output_paranoid} for alignment comparison.")

    def paranoid_align_multi(self, list_fail_samples, threads):  # noqa: C901
        l = len(list_fail_samples)
        with WorkerPool(n_jobs=threads, start_method="fork") as pool, tqdm(
            position=0,
            leave=True,
            desc="paranoid align...",
            total=l,
            unit="seqs",
            bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
        ) as pbar:
            for _ in pool.imap_unordered(self._align, list_fail_samples):
                pbar.update(1)

    def paranoid_check(self, refseqs, sample_data, dbm):  # noqa: C901
        """link to import_cached_samples

        return dict.
        """
        try:
            seq = list(refseqs[sample_data["sourceid"]])
        except Exception:
            refseqs[sample_data["sourceid"]] = list(
                dbm.get_sequence(sample_data["sourceid"])
            )
            seq = list(refseqs[sample_data["sourceid"]])
        prefix = ""

        sample_name = sample_data["name"]
        for vardata in dbm.iter_dna_variants(sample_name, sample_data["sourceid"]):
            if vardata["variant.alt"] == " ":
                for i in range(vardata["variant.start"], vardata["variant.end"]):
                    seq[i] = ""
            elif vardata["variant.start"] >= 0:
                seq[vardata["variant.start"]] = vardata["variant.alt"]
            else:
                prefix = vardata["variant.alt"]
        ref_name = sample_data["refmol"]
        # seq is now a restored version from variant dict.
        seq = prefix + "".join(seq)
        with open(sample_data["seq_file"], "r") as handle:
            orig_seq = handle.read()

        if seq != orig_seq:
            self.log("[Paranoid-test] Fail sample:" + sample_name)
            logging.warn(
                f"Fail in sanity check: This {sample_name} sample will not be inserted to the database...,"
                + "keeps an error log under the given cache directory."
            )
            if not os.path.exists(self.error_dir):
                os.makedirs(self.error_dir)
            with open(
                os.path.join(self.error_dir, f"{sample_name}.error.var"), "w+"
            ) as handle:
                for vardata in dbm.iter_dna_variants(
                    sample_name, sample_data["sourceid"]
                ):
                    handle.write(str(vardata) + "\n")

            qryfile = os.path.join(
                self.error_dir, sample_name + ".error.restored_sam.fa"
            )
            reffile = os.path.join(
                self.error_dir, sample_name + ".error.original_sam.fa"
            )

            with open(qryfile, "w+") as handle:
                handle.write(">seq\n" + seq)
            with open(reffile, "w+") as handle:
                handle.write(">ref\n" + orig_seq)
            output_paranoid = os.path.join(
                self.basedir, f"{sample_name}.withref.{ref_name}.fail-paranoid.fna"
            )

            dbm.delete_alignment(
                seqhash=sample_data["seqhash"], element_id=sample_data["sourceid"]
            )
            # delete sample  if this sample didnt have any alignment and variant??.
            _return_ali_id = dbm.get_alignment_by_seqhash(
                seqhash=sample_data["seqhash"]
            )
            if len(_return_ali_id) == 0:
                logging.warn("Sonar will delete a sample with empty alignment")
                dbm.delete_samples(sample_name)
                dbm.delete_seqhash(sample_data["seqhash"])

            return {
                "sample_name": sample_name,
                "qryfile": qryfile,
                "reffile": reffile,
                "output_paranoid": output_paranoid,
            }
        else:
            return {}

    def paranoid_test(self, refseqs, sample_data, dbm):  # noqa: C901
        """link to import_cached_samples
        The purpose of pranoid test is try to
        :Parameters:

            refseqs (dict): chracter list of reference sequence
            example;
            {1125: ['G', 'T', 'T', 'A', 'G', 'T
             'A', 'T', 'T', 'T', 'A', 'A', 'T'...]
             }

            sample_data (dict):
            example;
            {'name': 'OP764616.1', 'sampleid': 55, 'refmol': 'NC_003310.1',
            'refmolid': 5, 'sourceid': 1125, 'translationid': 1, 'algnid': None,
            'header': 'OP764616.1 |Monkeypox virus isolate MPXV/Germany/2022/RKI558, complete genome',
            'seqhash': 'bINAPXMjzqP+/fiyN/eEU0UgyKk',
            'seq_file': '/tmp_NC003_4sam/seq/Yk/YklOQVBYTr.seq',
            'ref_file': '/tmp_NC003_4sam/ref/NC_003310.1.seq',
            'tt_file': '/tmp_NC003_4sam/ref/1.tt',
            'algn_file': '/tmp_NC003_4sam/algn/Yk/YzMkJBT2srUGhHT0RXRQ.algn',
            'var_file': '/tmp_NC003_4sam/var/Yk/srUGhHT0RXRQ.var',
            'lift_file': '/mnt/c/works/data/mpx/tmp_NC003_4sam/ref/NC_003310.1.lift',
            'properties': {}}

        :Returns:

        Note>
            This process cause slow perfomance during checking
        """
        try:
            seq = list(refseqs[sample_data["sourceid"]])

        except Exception:
            # FIXED: change from refmolid to sourceid

            # เก็บค่า refseq *dict() ด้วย sourceid ซึ่งเป็นค่า DNA ทั้ฃหดมของ reference
            # ด้วย list
            refseqs[sample_data["sourceid"]] = list(
                dbm.get_sequence(sample_data["sourceid"])
            )
            # list of ref DNA
            # orignal code-:list(refseqs[sample_data["sourceid"]])
            seq = list(refseqs[sample_data["sourceid"]])
        # print()
        # print("-----####------ paranoid_test -----####------")
        # Ref sequence
        # print(seq)
        # print("-----####------ sourceid -----####------")
        # print(sample_data["sourceid"])
        # print("-----####------  -----####------")
        # print(sample_data["name"], sample_data["sourceid"])
        # so we get original seq (reference) and then we insert varaints afterward
        # self.log("reference seqeunce:" + str(seq))
        prefix = ""
        sample_name = sample_data["name"]
        # TODO: the problem arise here
        for vardata in dbm.iter_dna_variants(sample_name, sample_data["sourceid"]):
            # get all variants from this source ID and sample name
            if vardata["variant.alt"] == " ":
                for i in range(vardata["variant.start"], vardata["variant.end"]):
                    seq[i] = ""
            elif vardata["variant.start"] >= 0:
                seq[vardata["variant.start"]] = vardata["variant.alt"]
            else:
                prefix = vardata["variant.alt"]
        # print("-----####------ prefix -----####------")
        # print(prefix)
        ref_name = sample_data["refmol"]
        # seq is now a restored version from variant dict.
        seq = prefix + "".join(seq)

        # self.log("sample seqeunce:" + str(seq))

        with open(sample_data["seq_file"], "r") as handle:
            orig_seq = handle.read()
        if seq != orig_seq:
            logging.warn(
                f"Fail in sanity check: This {sample_name} sample will not be inserted to the database...,"
                + "keeps an error log under the given cache directory."
            )
            try:
                mismatch = [i for i, (a, b) in enumerate(zip(seq, orig_seq)) if a != b]
                # for i in range(len(orig_seq)):
                #    if orig_seq[i] != seq[i]:
                #        _lin.append(i)
                self.log("-----")
                self.log("Fail sample:" + sample_name)
                self.log("First position of mismatch:" + str(mismatch[0]))
                self.log(seq[mismatch[0]])
                self.log(orig_seq[mismatch[0]])
                self.log(str(sample_data))
            except Exception:
                pass

            with open(
                os.path.join(self.basedir, f"{sample_name}.error.var"), "w+"
            ) as handle:
                for vardata in dbm.iter_dna_variants(
                    sample_name, sample_data["sourceid"]
                ):
                    handle.write(str(vardata) + "\n")

            qryfile = os.path.join(self.basedir, sample_name + ".error.restored_sam.fa")
            reffile = os.path.join(self.basedir, sample_name + ".error.original_sam.fa")

            with open(qryfile, "w+") as handle:
                handle.write(">seq\n" + seq)
            with open(reffile, "w+") as handle:
                handle.write(">ref\n" + orig_seq)
            output_paranoid = f"{sample_name}.withref.{ref_name}.fail-paranoid.fna"
            if not os.path.exists(output_paranoid):
                aligner = sonarAligner(cache_outdir=self.basedir)

                qry, ref = aligner.align(qryfile, reffile)
                with open(output_paranoid, "w+") as handle:
                    handle.write(
                        ">original_"
                        + sample_name
                        + "\n"
                        + ref
                        + "\n>restored_"
                        + sample_name
                        + "\n"
                        + qry
                        + "\n"
                    )
            logging.warn(f"See {output_paranoid} for alignment comparison.")
            # delete alignment, sourceid = reference id
            dbm.delete_alignment(
                seqhash=sample_data["seqhash"], element_id=sample_data["sourceid"]
            )
            # delete sample  if this sample didnt have any alignment and variant??.
            #
            _return_ali_id = dbm.get_alignment_by_seqhash(
                seqhash=sample_data["seqhash"]
            )
            if len(_return_ali_id) == 0:
                logging.warn("Sonar will delete a sample with empty alignment")
                dbm.delete_samples(sample_name)
                dbm.delete_seqhash(sample_data["seqhash"])
            #
            """
            sys.exit(
                "import error: original sequence of sample "
                + sample_data["name"]
                + " cannot be restored from stored genomic profile for sample (see paranoid.alignment.fna)"
            )

            """
            return False
        else:
            return True


if __name__ == "__main__":
    pass
