"""
Small package of Python utilities for extracting and cleaning DASH13 data
from "ASCII files to be worked" directory.
"""

try:
    import pandas
except ImportError:
    print """This package depends upon the pandas package.  Please make
    sure that pandas is installed and is accessible from PYPATH.
    """
    raise

from ascii.extract import *
from ascii.clean import *
from ascii.db_funs import *

import ascii.dash13