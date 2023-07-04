#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Stephan Fuchs (Robert Koch Institute, MF1, fuchss@rki.de)
# , Kunaphas (RKI-HPI, kunaphas.kon@gmail.com)

# DEPENDENCIES
import collections
import csv
from datetime import datetime
import json
import os
import sys

from Bio import SeqIO
from mpire import WorkerPool
import pandas as pd
from tqdm import tqdm

from mpxsonar.annotation import read_sonar_hash
from mpxsonar.annotation import read_tsv_snpSift
from . import __version__
from . import logging
from .align import sonarAligner
from .cache import sonarCache
from .dbm import sonarDBManager
from .utils import harmonize


# CLASS
class sonarBasics(object):
    """
    this object provides sonarBasics functionalities and intelligence
    """

    def __init__(self):
        pass
        # logging.basicConfig(format="%(asctime)s %(message)s")

    @staticmethod
    def get_version():
        return __version__

    # DB MAINTENANCE

    # @staticmethod
    # def get_module_base(*join_with):
    #    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *join_with)

    @staticmethod
    def setup_db(  # noqa: C901
        url,
        default_setup=True,
        reference_gb=None,
        debug=False,
        quiet=False,
    ):
        try:
            sonarDBManager.setup(url, debug=debug)

            # loading default data
            if default_setup:
                with sonarDBManager(url, readonly=False, debug=debug) as dbm:
                    # adding pre-defined sample properties
                    dbm.add_property(
                        "imported",
                        "date",
                        "date",
                        "date sample has been imported to the database",
                        "sample",
                    )
                    dbm.add_property(
                        "modified",
                        "date",
                        "date",
                        "date when sample data has been modified lastly",
                        "sample",
                    )
                    dbm.add_property(
                        "SEQ_TECH",
                        "text",
                        "text",
                        "stores the sequencing technologies.",
                        "sample",
                    )
                    dbm.add_property(
                        "LENGTH",
                        "integer",
                        "numeric",
                        "stores the genome lenght",
                        "sample",
                    )
                    dbm.add_property(
                        "GEO_LOCATION",
                        "text",
                        "text",
                        "stores the GEO location",
                        "sample",
                    )
                    dbm.add_property(
                        "COUNTRY",
                        "text",
                        "text",
                        "stores a country",
                        "sample",
                    )
                    dbm.add_property(
                        "GENOME_COMPLETENESS",
                        "text",
                        "text",
                        "stores genome completeness",
                        "sample",
                    )
                    dbm.add_property(
                        "COLLECTION_DATE",
                        "date",
                        "date",
                        "stores the sample collection date",
                        "sample",
                    )
                    # adding reference
                    if not reference_gb:
                        reference_gb = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            "data",
                            "NC_063383.1.gb",
                        )
                    # adding reference
                    sonarBasics().add_ref_by_genebank_file(
                        url, reference_gb, debug=debug
                    )

                    if not quiet:
                        logging.info("Success: Database was successfully installed")
        except Exception as e:
            logging.exception(e)
            logging.error("Database was fail to create")
            sys.exit()

    @staticmethod
    def add_ref_by_genebank_file(db_url, reference_gb, debug=False):
        """
        add reference
        """
        with sonarDBManager(db_url, readonly=False, debug=debug) as dbm:
            try:
                records = [x for x in sonarBasics.iter_genbank(reference_gb)]
                ref_id = dbm.add_reference(
                    records[0]["accession"],
                    records[0]["description"],
                    records[0]["organism"],
                    1,
                    1,
                )

                # adding reference molecule and elements
                for i, record in enumerate(records):
                    gene_ids = {}
                    s = 1 if i == 0 else 0
                    mol_id = dbm.insert_molecule(
                        ref_id,
                        record["moltype"],
                        record["accession"],
                        record["symbol"],
                        record["description"],
                        i,
                        record["length"],
                        s,
                    )
                    # source handling
                    source_id = dbm.insert_element(
                        mol_id,
                        "source",
                        record["source"]["accession"],
                        record["source"]["symbol"],
                        record["source"]["description"],
                        record["source"]["start"],
                        record["source"]["end"],
                        record["source"]["strand"],
                        record["source"]["sequence"],
                        standard=1,
                        parts=record["source"]["parts"],
                    )
                    if record["source"]["sequence"] != dbm.get_sequence(source_id):
                        sys.exit(
                            "genbank error-1: could not recover sequence of '"
                            + record["source"]["accession"]
                            + "' (source)"
                        )
                    # gene handling
                    for elem in record["gene"]:
                        # we should query with accession number to distinguish query
                        # when gene name is same
                        gene_ids[elem["accession"]] = dbm.insert_element(
                            mol_id,
                            "gene",
                            elem["accession"],
                            elem["symbol"],
                            elem["description"],
                            elem["start"],
                            elem["end"],
                            elem["strand"],
                            elem["sequence"],
                            standard=0,
                            parent_id=source_id,
                            parts=elem["parts"],
                        )
                        if elem["sequence"] != dbm.extract_sequence(
                            gene_ids[elem["accession"]], molecule_id=mol_id
                        ):
                            print(elem["sequence"])
                            print(gene_ids)
                            sys.exit(
                                "genbank error-2: could not recover sequence of '"
                                + elem["accession"]
                                + "' (gene)"
                            )

                    # cds handling
                    for elem in record["cds"]:
                        cid = dbm.insert_element(
                            mol_id,
                            "cds",
                            elem["accession"],
                            elem["symbol"],
                            elem["description"],
                            elem["start"],
                            elem["end"],
                            elem["strand"],
                            elem["sequence"],
                            0,
                            gene_ids[elem["gene"]],
                            elem["parts"],
                        )
                        if elem["sequence"] != dbm.extract_sequence(
                            cid, translation_table=1, molecule_id=mol_id
                        ):
                            sys.exit(
                                "genbank error-3: could not recover sequence of '"
                                + elem["accession"]
                                + "' (cds)"
                            )
                return 0
            except Exception as e:
                logging.exception(e)
                logging.error("Fail to process GeneBank file")
                raise

    # DATA IMPORT
    # genbank handling handling
    @staticmethod
    def process_segments(feat_location_parts, cds=False):
        base = 0
        div = 1 if not cds else 3
        segments = []
        for i, segment in enumerate(feat_location_parts, 1):
            segments.append(
                [int(segment.start), int(segment.end), segment.strand, base, i]
            )
            base += round((segment.end - segment.start - 1) / div, 1)
        return segments

    @staticmethod
    def iter_genbank(fname):  # noqa: C901
        """
        small note on iter_genbank function
        1. At CDS and gene type, if "gene" key is not exist in dict, we use locus_tag instead.
        https://www.ncbi.nlm.nih.gov/genomes/locustag/Proposal.pdf. This also apply to accession
        in similar way.

        """
        gb_data = {}
        for gb_record in SeqIO.parse(fname, "genbank"):
            # adding general annotation
            gb_data["accession"] = (
                gb_record.name + "." + str(gb_record.annotations["sequence_version"])
            )
            gb_data["symbol"] = (
                gb_record.annotations["symbol"]
                if "symbol" in gb_record.annotations
                else ""
            )
            gb_data["organism"] = gb_record.annotations["organism"]
            gb_data["moltype"] = None
            gb_data["description"] = gb_record.description
            gb_data["length"] = None
            gb_data["segment"] = ""
            gb_data["gene"] = []
            gb_data["cds"] = []
            gb_data["source"] = None

            # adding source annotation
            source = [x for x in gb_record.features if x.type == "source"]
            if len(source) != 1:
                sys.exit(
                    "genbank error: expecting exactly one source feature (got: "
                    + str(len(source))
                    + ")"
                )
            feat = source[0]
            gb_data["moltype"] = (
                feat.qualifiers["mol_type"][0] if "mol_type" in feat.qualifiers else ""
            )
            gb_data["source"] = {
                "accession": gb_data["accession"],
                "symbol": gb_data["accession"],
                "start": int(feat.location.start),
                "end": int(feat.location.end),
                "strand": "",
                "sequence": harmonize(feat.extract(gb_record.seq)),
                "description": "",
                "parts": sonarBasics.process_segments(feat.location.parts),
            }
            gb_data["length"] = len(gb_data["source"]["sequence"])
            if "segment" in feat.qualifiers:
                gb_data["segment"] = feat.qualifiers["segment"][0]
            try:
                for feat in gb_record.features:
                    # adding gene annotation
                    if feat.type == "gene":
                        # pseudogene is unknown
                        if "pseudogene" in feat.qualifiers:
                            continue
                        if feat.id != "<unknown id>":
                            accession = feat.id
                        elif "gene" in feat.qualifiers:
                            accession = feat.qualifiers["gene"][0]
                        elif "locus_tag" in feat.qualifiers:
                            accession = feat.qualifiers["locus_tag"][0]

                        if "gene" in feat.qualifiers:
                            symbol = feat.qualifiers["gene"][0]
                        else:
                            symbol = feat.qualifiers["locus_tag"][0]
                        gb_data["gene"].append(
                            {
                                "accession": accession,
                                "symbol": symbol,
                                "start": int(feat.location.start),
                                "end": int(feat.location.end),
                                "strand": feat.strand,
                                "sequence": harmonize(
                                    feat.extract(gb_data["source"]["sequence"])
                                ),
                                "description": "",
                                "parts": sonarBasics.process_segments(
                                    feat.location.parts
                                ),
                            }
                        )
                    # adding cds annotation
                    elif feat.type == "CDS":
                        parts = sonarBasics.process_segments(feat.location.parts, True)
                        # when pseudogene is unknown
                        if "pseudogene" in feat.qualifiers:
                            continue
                        # when gene symbol is not available.
                        if "gene" in feat.qualifiers:
                            symbol = feat.qualifiers["gene"][0]
                        else:
                            symbol = feat.qualifiers["locus_tag"][0]

                        gb_data["cds"].append(
                            {
                                "accession": feat.qualifiers["protein_id"][0],
                                "symbol": symbol,
                                "start": int(feat.location.start),
                                "end": int(feat.location.end),
                                "strand": feat.strand,
                                "gene": symbol,
                                "sequence": feat.qualifiers["translation"][0],
                                "description": feat.qualifiers["product"][0],
                                "parts": parts,
                            }
                        )
                        if sum([abs(x[1] - x[0]) for x in parts]) % 3 != 0:
                            sys.exit(
                                "gbk error: length of cds '"
                                + feat.qualifiers["protein_id"][0]
                                + "' is not a multiple of 3 ("
                                + str(sum([abs(x[1] - x[2]) for x in parts]))
                                + ")."
                            )

            except KeyError as e:
                logging.exception(e)
                logging.error("-----------")
                print(feat)
                raise

            yield gb_data

    # importing
    @staticmethod
    def get_csv_colnames(fname, delim=","):
        with open(fname, "r") as handle:
            csvdict = csv.DictReader(handle, delimiter=delim)
            return list(csvdict.fieldnames)

    @staticmethod
    def import_data(  # noqa: C901
        db,
        fasta=[],
        csv_files=[],
        tsv_files=[],
        cols=[],
        cachedir=None,
        autolink=False,
        progress=False,
        update=True,
        threads=1,
        debug=False,
        quiet=False,
        reference=None,
    ):
        if not quiet:
            if not update:
                logging.info("import mode: skipping existing samples")
            else:
                logging.info("import mode: updating existing samples")

        if not fasta:
            if (not tsv_files and not csv_files) or not update:
                logging.info("Nothing to import.")
                exit(0)

        # prop handling
        with sonarDBManager(db, readonly=True) as dbm:
            db_properties = set(dbm.properties.keys())
            db_properties.add("sample")

        propnames = {x: x for x in db_properties} if autolink else {}

        # csv/tsv file processing
        properties = collections.defaultdict(dict)
        metafiles = [(x, ",") for x in csv_files] + [(x, "\t") for x in tsv_files]
        if metafiles:
            for x in cols:
                if x.count("=") != 1:
                    sys.exit(
                        "input error: "
                        + x
                        + " is not a valid sample property assignment."
                    )
                k, v = x.split("=")
                if k == "SAMPLE":
                    k = "sample"
                if k not in db_properties:
                    sys.exit(
                        "input error: sample property "
                        + k
                        + " is unknown to the selected database. Use list-props to see all valid properties."
                    )
                propnames[k] = v
                propnamekeys = sorted(propnames.keys())
            if "sample" not in propnames:
                sys.exit("input error: a sample column has to be assigned.")

            for fname, delim in metafiles:
                with open(fname, "r") as handle, tqdm(
                    desc="processing " + fname + "...",
                    total=os.path.getsize(fname),
                    unit="bytes",
                    unit_scale=True,
                    bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
                    disable=not progress,
                ) as pbar:
                    print("\n")
                    line = handle.readline()
                    pbar.update(len(line))
                    fields = sonarBasics.get_csv_colnames(fname, delim)
                    # logging.info(f"Read Header:{fields}")
                    cols = {}
                    if not quiet:
                        print("linking data from:", fname)
                    for x in propnamekeys:
                        c = fields.count(propnames[x])
                        if c == 1:
                            cols[x] = fields.index(propnames[x])
                            if not quiet:
                                print("  " + x + " <- " + propnames[x])
                        elif c > 1:
                            sys.exit(
                                "error: " + propnames[x] + " is not an unique column."
                            )
                    if "sample" not in cols:
                        sys.exit(
                            "error: tsv file does not contain required sample column."
                        )
                    elif len(cols) == 1:
                        sys.exit(
                            "input error: tsv does not provide any informative column."
                        )
                    for line in handle:
                        pbar.update(len(line))
                        fields = line.strip("\r\n").split("\t")
                        sample = fields[cols["sample"]]
                        for x in cols:
                            if x == "sample":
                                continue
                            properties[sample][x] = fields[cols[x]]

        # setup cache
        cache = sonarCache(
            db,
            outdir=cachedir,
            logfile="import.log",
            allow_updates=update,
            temp=not cachedir,
            debug=debug,
            disable_progress=not progress,
            refacc=reference,
        )
        # logging.info(print_max_min_rule(cache.get_refseq(reference)))
        # importing sequences
        if fasta:
            cache.add_fasta(*fasta, propdict=properties)
            aligner = sonarAligner(cache_outdir=cachedir)
            l = len(cache._samplefiles_to_profile)
            # start alignment
            with WorkerPool(n_jobs=threads, start_method="fork") as pool, tqdm(
                desc="profiling sequences...",
                total=l,
                unit="seqs",
                bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
                disable=not progress,
            ) as pbar:
                for _ in pool.imap_unordered(
                    aligner.process_cached_sample, cache._samplefiles_to_profile
                ):
                    pbar.update(1)
            # insert into DB
            cache.import_cached_samples(threads)

        # importing properties
        if metafiles:
            logging.info("Import meta data...")
            with sonarDBManager(db, readonly=False, debug=debug) as dbm:
                for sample_name in tqdm(
                    properties,
                    desc="import data ...",
                    total=len(properties),
                    unit="samples",
                    bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
                    disable=not progress,
                ):
                    sample_id = dbm.get_sample_id(sample_name)
                    if not sample_id:
                        continue
                    for property_name, value in properties[sample_name].items():
                        dbm.insert_property(sample_id, property_name, value)

        cache.log(f"//Done:--{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}--")

    # matching
    @staticmethod
    def match(
        db,
        profiles=[],
        reserved_props_dict={},
        propdict={},
        reference=None,
        outfile=None,
        output_column="all",
        format="csv",
        debug="False",
        showNX=False,
        ignoreTerminalGaps=True,
    ):
        # print(profiles)
        with sonarDBManager(db, debug=debug) as dbm:
            if format == "vcf" and reference is None:
                reference = dbm.get_default_reference_accession()
                logging.info(f"Query using default reference: {reference}")
            elif format != "vcf" and reference is None:
                # retrieve all references
                # reference = None
                logging.info("Query using reference: all references")
            else:
                logging.info(f"Query using reference: {reference}")

            cursor = dbm.match(
                *profiles,
                reserved_props=reserved_props_dict,
                properties=propdict,
                reference_accession=reference,
                format=format,
                output_column=output_column,
                showNX=showNX,
                ignoreTerminalGaps=ignoreTerminalGaps,
            )
            if format == "csv" or format == "tsv":
                logging.info("Total result: " + str(len(cursor)))
                tsv = True if format == "tsv" else False
                sonarBasics.exportCSV(
                    cursor, outfile=outfile, na="*** no match ***", tsv=tsv
                )
            elif format == "count":
                if outfile:
                    with open(outfile, "w") as handle:
                        handle.write(str(cursor.fetchone()["count"]))
                else:
                    print(cursor.fetchone()["count"])
            elif format == "vcf":
                sonarBasics.exportVCF(
                    cursor, reference=reference, outfile=outfile, na="*** no match ***"
                )
            else:
                sys.exit("error: '" + format + "' is not a valid output format")

    # restore
    @staticmethod
    def restore(  # noqa: C901
        db, *samples, reference_accession=None, aligned=False, outfile=None, debug=False
    ):
        with sonarDBManager(db, readonly=True, debug=debug) as dbm:
            if not samples:
                samples = [x for x in dbm.iter_sample_names()]
            if not samples:
                print("No samples stored in the given database.")
                sys.exit(0)
            handle = sys.stdout if outfile is None else open(outfile, "w")
            gap = "-" if aligned else ""
            gapalts = {" ", "."}
            for sample in samples:
                prefixes = collections.defaultdict(str)
                molecules = {
                    x["element.id"]: {
                        "seq": list(x["element.sequence"]),
                        "mol": x["element.symbol"],
                    }
                    for x in dbm.get_alignment_data(
                        sample, reference_accession=reference_accession
                    )
                }
                # gap = "-" if aligned else ""
                for vardata in dbm.iter_dna_variants(sample, *molecules.keys()):
                    if aligned and len(vardata["variant.alt"]) > 1:
                        vardata["variant.alt"] = (
                            vardata["variant.alt"][0]
                            + vardata["variant.alt"][1:].lower()
                        )
                    if vardata["variant.alt"] in gapalts:
                        for i in range(
                            vardata["variant.start"], vardata["variant.end"]
                        ):
                            molecules[vardata["element.id"]]["seq"][i] = gap
                    elif vardata["variant.start"] >= 0:

                        molecules[vardata["element.id"]]["seq"][
                            vardata["variant.start"]
                        ] = vardata["variant.alt"]
                    else:
                        prefixes[vardata["element.id"]] = vardata["variant.alt"]
                molecules_len = len(molecules)
                records = []
                for element_id in molecules:
                    if molecules_len == 1:
                        records.append(">" + sample)
                    else:
                        records.append(
                            ">"
                            + sample
                            + " [molecule="
                            + molecules[vardata["element.id"]]["mol"]
                            + "]"
                        )
                    records.append(
                        prefixes[element_id]
                        + "".join(molecules[vardata["element.id"]]["seq"])
                    )
                if len(records) > 0:
                    handle.write("\n".join(records) + "\n")

    # delete
    @staticmethod
    def delete(db, *samples, debug):
        with sonarDBManager(db, readonly=False, debug=debug) as dbm:
            before = dbm.count_samples()
            dbm.delete_samples(*samples)
            after = dbm.count_samples()
            logging.info(
                " %d of %d samples found and deleted."
                " %d samples remain in the database."
                % (before - after, len(samples), after)
            )

    # delete reference
    @staticmethod
    def del_ref(db, reference, debug):
        logging.info("Start to delete....the process is not reversible.")
        with sonarDBManager(db, readonly=False, debug=debug) as dbm:

            # remove alignment
            samples_ids = dbm.get_samples_by_ref(reference)
            logging.info(
                f"{len(samples_ids)} sample that linked to the reference will be also deleted"
            )
            # delete only reference will also delete the whole related data.
            """
            if samples_ids:
                if debug:
                    logging.info(f"Delete: {samples_ids}")
                for sample in samples_ids:
                    # dbm.delete_seqhash(sample["seqhash"])
                    dbm.delete_alignment(
                        seqhash=sample["seqhash"], element_id=_ref_element_id
                    )
            """
            dbm.delete_reference(reference)

    @staticmethod
    def show_db_info(db):
        with sonarDBManager(db, readonly=True) as dbm:
            print("MPXSonar Version: ", sonarBasics.get_version())
            # print("database path:             ", dbm.dbfile)
            print("database version: ", dbm.get_db_version())
            print("database size: ", dbm.get_db_size())
            print("unique samples: ", dbm.count_samples())
            print("unique sequences: ", dbm.count_sequences())
            # print("Sample properties          ", dbm.get_earliest_import())
            # print("latest genome import:      ", dbm.get_latest_import())
            # print("earliest sampling date:    ", dbm.get_earliest_date())
            # print("latest sampling date:      ", dbm.get_latest_date())

    # output
    # profile generation
    @staticmethod
    def iter_formatted_match(cursor):  # pragma: no cover
        """
        VCF output
        @deprecated("use another method")
        this will be removed soon
        """
        nuc_profiles = collections.defaultdict(list)
        aa_profiles = collections.defaultdict(list)
        samples = set()
        logging.warning("getting profile data")
        logging.warning("processing profile data")
        for row in cursor:

            samples.add(row["samples"])
            if row["element.type"] == "cds":
                aa_profiles[row["samples"]].append(
                    (
                        row["element.id"],
                        row["variant.start"],
                        row["element.symbol"] + ":" + row["variant.label"],
                    )
                )
            else:
                nuc_profiles[row["samples"]].append(
                    (row["element.id"], row["variant.start"], row["variant.label"])
                )
        out = []
        for sample in sorted(samples):
            print(sorted(nuc_profiles[sample], key=lambda x: (x[0], x[1])))

        logging.warning("assembling profile data")
        for sample in sorted(samples):
            out.append(
                {
                    "sample.name": sample,
                    "nuc_profile": " ".join(
                        sorted(nuc_profiles[sample], key=lambda x: (x[0], x[1]))
                    ),
                    "aa_profile": " ".join(
                        sorted(aa_profiles[sample], key=lambda x: (x[0], x[1]))
                    ),
                }
            )
        return out

    # csv
    def exportCSV(cursor, outfile=None, na="*** no data ***", tsv=False):
        i = -1
        try:
            for i, row in enumerate(cursor):
                if i == 0:
                    outfile = sys.stdout if outfile is None else open(outfile, "w")
                    sep = "\t" if tsv else ","
                    writer = csv.DictWriter(
                        outfile, row.keys(), delimiter=sep, lineterminator=os.linesep
                    )
                    writer.writeheader()
                writer.writerow(row)
            if i == -1:
                print(na)
        except Exception:
            logging.error("An exception occurred %s", row)
            raise

    # vcf
    def exportVCF(cursor, reference, outfile=None, na="*** no match ***"):  # noqa: C901
        """
        This function is used to output vcf file and hash.sonar file

        Note:
            * One ref. per vcf
            * POS position in VCF format: 1-based position
            * Deletion? In the VCF file, the REF allele represents the reference sequence
            before the deletion, and the ALT allele represents the deleted sequence
            example:suppose we have
                Ref: atCga C is the reference base
                1:   atGga C base is changed to G
                2:   at-ga C base is deleted w.r.t. the ref.
            #CHROM  POS     ID      REF     ALT
            1       3       .       C       G
            1       2       .       TC      T

        """
        records = collections.OrderedDict()
        all_samples = set()
        sample_hash_list = {}
        IDs_list = {}

        for row in cursor.fetchall():  # sonarBasics.iter_formatted_match(cursor):
            # print(row)
            element_id, variant_id, chrom, pos, pre_ref, ref, alt, samples, seqhash = (
                row["element.id"],
                row["variant.id"],
                row["molecule.accession"],
                row["variant.start"],
                row["variant.pre_ref"],
                row["variant.ref"],
                row["variant.alt"],
                row["samples"],
                row["seqhash"],
            )
            # POS position in VCF format: 1-based position
            pos = pos + 1
            # print(chrom, pos, ref, alt, samples)
            # reference ID is used just for now
            if chrom not in records:
                records[chrom] = collections.OrderedDict()
            if pos not in records[chrom]:
                records[chrom][pos] = {}

            if ref not in records[chrom][pos]:
                records[chrom][pos][ref] = {}

            if pre_ref not in records[chrom][pos]:
                records[chrom][pos]["pre_ref"] = pre_ref

            if alt not in records[chrom][pos][ref]:
                records[chrom][pos][ref][alt] = []
            records[chrom][pos][ref][alt].append(samples)  # set(samples.split("\t"))

            # print(records)
            all_samples.update(samples.split("\t"))

            # handle the variant and sample.
            if samples not in IDs_list:
                IDs_list[samples] = []
            IDs_list[samples].append(
                {"element_id": element_id, "variant_id": variant_id}
            )

            # handle the hash and sample.
            sample_hash_list[samples] = seqhash

        # print(records)
        if len(records) != 0:
            all_samples = sorted(all_samples)

            if outfile is None:
                handle = sys.stdout
            else:
                # if not outfile.endswith(".gz"):
                # outfile += ".gz"

                # Combine sonar_hash and reference into a single dictionary
                data = {
                    "sample_variantTable": IDs_list,
                    "sample_hashes": sample_hash_list,
                    "reference": reference,
                }
                # Remove the existing extension from outfile and then append a new extension.
                filename = os.path.splitext(outfile)[0] + ".sonar_hash"
                with open(filename, "w") as file:
                    json.dump(data, file)
                    logging.info(
                        f"sample list output: '{filename}', this file is used when you want to reimport annotated data back to the database."
                    )
                handle = open(outfile, mode="w")  # bgzf.open(outfile, mode='wb')

            # vcf header
            handle.write("##fileformat=VCFv4.2\n")
            handle.write(
                "##CreatedDate=" + datetime.now().strftime("%d/%m/%Y,%H:%M:%S") + "\n"
            )
            handle.write("##Source=MpoxSonar" + sonarBasics().get_version() + "\n")
            # handle.write("##sonar_sample_hash="+str(sample_hash_list)+"\n")
            handle.write("##reference=" + reference + "\n")
            handle.write(
                '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
            )
            handle.write(
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t"
                + "\t".join(all_samples)
                + "\n"
            )
            # records
            for chrom in records:
                for pos in records[chrom]:
                    for ref in records[chrom][pos]:
                        if ref == "pre_ref":  # skip pre_ref key
                            continue
                        # snps and inserts (combined output)
                        alts = [x for x in records[chrom][pos][ref].keys() if x.strip()]
                        if alts:
                            alt_samples = set()
                            gts = []
                            for alt in alts:
                                samples = records[chrom][pos][ref][alt]
                                # print(samples)

                                gts.append(
                                    ["1" if x in samples else "0" for x in all_samples]
                                )
                                alt_samples.update(samples)

                            # NOTE: this code part produce 0/1, 1/0
                            gts = [
                                ["0" if x in alt_samples else "1" for x in all_samples]
                            ] + gts

                            record = [
                                chrom,
                                str(pos),
                                ".",
                                ref,
                                ",".join(alts),
                                ".",
                                ".",
                                ".",
                                "GT",
                            ] + ["/".join(x) for x in zip(*gts)]

                        # dels (individual output)
                        for alt in [
                            x for x in records[chrom][pos][ref].keys() if not x.strip()
                        ]:
                            pre_ref = records[chrom][pos]["pre_ref"]
                            samples = records[chrom][pos][ref][alt]
                            record = [
                                chrom,
                                str(
                                    pos - 1
                                ),  # -1 to the position for DEL, NOTE: be careful for 0-1=-1
                                ".",
                                (pre_ref + ref),
                                (pre_ref) if alt == " " else alt,  # changed form '.'
                                ".",
                                ".",
                                ".",
                                "GT",
                            ] + ["0/1" if x in samples else "./." for x in all_samples]
                        handle.write("\t".join(record) + "\n")
            handle.close()
        else:
            print(na)

    @staticmethod
    def set_key(dictionary, key, value):
        if key not in dictionary:
            dictionary[key] = value
        elif type(dictionary[key]) == list:
            dictionary[key].append(value)
        else:
            dictionary[key] = [dictionary[key], value]
        return dictionary

    @staticmethod
    def process_annotation(db, paired_list, progress=False):
        """

        Steps:
            1. Read annotated txt file and .sonar_hash
            2. Get alignment ID and source element ID
            3. Get variant ID
            4. Insert the 3 IDs into the database.

        Input:
            paired_list = (annotated_file, sonar_hash_file)

        """
        with sonarDBManager(db, readonly=False) as dbm:
            for _tuple in tqdm(
                paired_list,
                desc="Importing data...",
                total=len(paired_list),
                unit="samples",
                bar_format="{desc} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {elapsed}<{remaining}, {rate_fmt}{postfix}]",
                disable=progress,
            ):
                annotated_file, sonar_hash_file = _tuple
                annotated_df = read_tsv_snpSift(annotated_file)
                sonar_hash = read_sonar_hash(sonar_hash_file)

                reference_accession = sonar_hash["reference"]
                sample_dict = sonar_hash["sample_hashes"]
                sample_variant_dict = sonar_hash["sample_variantTable"]

                # Step 2
                for sample_key in sample_dict:
                    hash_value = sample_dict[sample_key]
                    source_ids_list = dbm.get_element_ids(reference_accession, "source")

                    if len(source_ids_list) > 1:
                        logging.error("There is a duplicated element ID!!")
                        sys.exit(1)
                    else:
                        source_element_id = source_ids_list[0]

                    alnids = dbm.get_alignment_id(hash_value, source_element_id)

                    if type(alnids) is list:
                        logging.error(
                            f"Hash value: {hash_value} is not found in the database!!"
                        )
                        sys.exit(1)
                    else:
                        alignment_id = alnids

                    # Step 3
                    sample_variant_list = sample_variant_dict[sample_key]

                    # NOTE: MemoryError can be raised if a huge list is converted to a DataFrame
                    _df = pd.DataFrame.from_dict(sample_variant_list)

                    for row in _df.itertuples():
                        variant_id = getattr(row, "variant_id")

                        selected_var = dbm.get_variant_by_id(variant_id)
                        # ref = selected_var["ref"]
                        # VCF: 1-based position
                        # For DEL, we dont +1
                        ref = (
                            (selected_var["pre_ref"] + selected_var["ref"])
                            if selected_var["alt"] == " "
                            else selected_var["ref"]
                        )
                        start = (
                            selected_var["start"]
                            if selected_var["alt"] == " "
                            else selected_var["start"] + 1
                        )
                        alt = (
                            selected_var["pre_ref"]
                            if selected_var["alt"] == " "
                            else selected_var["alt"]
                        )

                        # Check if it exists in the annotated txt file.
                        selected_row = annotated_df.loc[
                            (annotated_df["POS"] == start)
                            & (annotated_df["REF"] == ref)
                            & (annotated_df["ALT"] == alt)
                        ]
                        # If it does not return any result or more than 1, we should raise an error because
                        # the wrong annotated text file is being used or the database has already been modified.
                        if len(selected_row) != 1:
                            logging.error(
                                "It appears that the wrong annotated text file is being used "
                                "or the .sonar_hash file is not match to the input "
                                "or the database has already been modified. Please double-check the file "
                                "or database!"
                            )
                            logging.debug("Get VAR:")
                            logging.debug(selected_var)
                            logging.debug("Use for searching a ROW:")
                            logging.debug(f"start:{start} , ref:{ref} , alt:{alt}")
                            logging.debug("Get DF:")
                            print(f"{annotated_df[annotated_df['POS'] == start]}")
                            sys.exit(1)

                        # Find associated ID from annotationTable.
                        effects = selected_row["EFFECT"].values[0]
                        effects = effects.split(",")
                        for effect in effects:
                            if effect is None or effect == ".":
                                effect = ""  # Default
                            effect_id = dbm.get_annotation_ID_by_type(effect)

                            # Step 4
                            # Insert into the database
                            dbm.insert_alignment2annotation(
                                variant_id, alignment_id, effect_id
                            )
