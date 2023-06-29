import gzip
import lzma
import os
import sys

from Bio.SeqUtils.CheckSum import seguid


def print_max_min_rule(ref):
    up = int((len(ref) * 100.3) / 100)
    low = int((len(ref) * 99.7) / 100)
    return f"Accept lenght:{low}<{len(ref)}<{up}"


def check_seq_compact(ref, qry):
    qry_size = len(qry)
    up = int((len(ref) * 100.3) / 100)
    low = int((len(ref) * 99.7) / 100)
    if low < qry_size and qry_size < up:
        return True
    else:
        return False


def hash(seq):
    """ """
    return seguid(seq)


def harmonize(seq):
    """ """
    return str(seq).strip().upper().replace("U", "T")


def open_file(fname, mode="r", compressed=False, encoding=None):
    if not os.path.isfile(fname):
        sys.exit("input error: " + fname + " does not exist.")
    if compressed == "auto":
        compressed = os.path.splitext(fname)[1][1:]
    try:
        if compressed == "gz":
            return gzip.open(fname, mode + "t", encoding=encoding)
        if compressed == "xz":
            return lzma.open(fname, mode + "t", encoding=encoding)
        else:
            return open(fname, mode, encoding=encoding)
    except Exception:
        sys.exit("input error: " + fname + " cannot be opened.")


def insert_before_keyword(s, keyword, new_string):
    """
    Inserts a string before a keyword in a string.

    Args:
        s (str): The original string.
        keyword (str): The keyword to search for in the string.
        new_string (str): The string to insert before the keyword.

    Returns:
        str: The modified string.
    """
    # Find the index of the keyword in the string
    index = s.find(keyword)

    # If the keyword is not found, return the original string
    if index == -1:
        return s

    # Insert the new string before the keyword
    modified_string = s[:index] + new_string + s[index:]

    return modified_string


def calculate_mutation_type_DNA(ref, alt):
    """
    example cases;
    1. C>T SNV
    2. T>TTT (insert two positions) frameshift
    3. TAG> deleltion
    4. A>AGGG insertion
    5. T> frameshift
    6. A>AGAAGTAGAA insertion
    7. >A frameshift
    # The
    Returns:
        str: The NT variant type. (SNV,DEL,INS,frameshift,unknown)
    """
    # to remove empty space from string ' '
    ref = ref.replace(" ", "")
    ref_len = len(ref)
    alt = alt.replace(" ", "")
    alt_len = len(alt)

    if ref_len == alt_len:
        return "SNV"
    elif ref_len != alt_len:  # INSERTION
        if ref_len < alt_len:

            if ref_len == 0:  # when the ref is empty
                if alt_len % 3 != 0:
                    return "frameshift"
                else:
                    return "INS"
            else:
                # need to ignore a first position at 'alt' before
                # doing a calucation.
                # (T>TTT, in this case TT will be counted only )
                alt_len = len(alt[1:])

                if alt_len % 3 != 0:
                    return "frameshift"
                else:
                    return "INS"

        elif ref_len > alt_len:  # DELETION
            if ref_len % 3 != 0:
                return "frameshift"
            else:
                return "DEL"
        else:
            return "unknown"
    else:
        return "unknown"
