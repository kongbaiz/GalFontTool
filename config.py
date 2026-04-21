import sys

try:
    import opencc

    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False

try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
