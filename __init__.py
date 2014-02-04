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

from dash13.extract import *
from dash13.clean import *
from dash13.db_funs import *

import dash13.d13_dbf
