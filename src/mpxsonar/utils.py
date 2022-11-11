import gzip
import lzma
import os
import sys

from Bio.SeqUtils.CheckSum import seguid


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
