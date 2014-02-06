# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:57:02 2014

@author: Huston Bokinsky
"""

import pandas
from . import defaults as DEF

def toDataFrame(rl):
    """
    Return pandas.DataFrame indexed by recId from Record list.
    @type  rl: list
    @param rl: list of Records
    @rtype: pandas.DataFrame
    """
    d = [(r.recId, r.wholerec) for r in rl]
    return pandas.DataFrame.from_items(d, orient='index',
            columns=DEF.__ascii_fields__)

def merge(df1, df2):
    """
    Return pandas.DataFrame merged from <df1> and <df2>.
    
    @type  df1, df2: pandas.DataFrame
    @param df1, df2: dataframes indexed by recId
    @return: pandas.DataFrame
    """
    return pandas.merge(df1, df2, how='outer',
                        left_index=True, right_index=True)

