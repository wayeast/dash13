# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:57:02 2014

@author: Huston Bokinsky
"""

import pandas
from . import defaults as DEF
from . import clean as clean
from . import extract as extract

def toDataFrame(rl, col_names):
    """
    Return pandas.DataFrame indexed by recId from Record list.
    @type  rl: list
    @param rl: list of Records
    @rtype: pandas.DataFrame
    """
    d = [(r.recId, tuple([r.recId]) + r.wholerec) for r in rl]
    return pandas.DataFrame.from_items(d, orient='index',
            columns=col_names)

def merge_by_id(df1, df2):
    """
    Return pandas.DataFrame merged from <df1> and <df2>.
    
    @type  df1, df2: pandas.DataFrame
    @param df1, df2: dataframes indexed by recId
    @return: pandas.DataFrame
    """
    return pandas.merge(df1, df2, how='outer',
                        left_index=True, right_index=True)

merge_cols = [
'REC_ID',
'SYS_CODE',
'AC_MODL',
'EI_ID', 
'FAULTDAT',
'FAULTNO',
'SS']
def merge_ascii(df1, df2):
    """Merge records from FAU and ACT files into one dataframe.
    
    This accounts for the discrepancies in CORRDATE and WUC fields by
    preferring the earlier CORRDATE and the WUC value from an FAU
    file.
    
    @type df1, df2: pandas.DataFrame
    @param df1, df2: fau and act dataframes, respectively
    @return: pandas.DataFrame of values merged
    
    """
    draft = pandas.merge(df1, df2, 
                         how="outer", 
                         on=merge_cols, 
                         suffixes=('_fau', '_act'))
    draft['CORRDATE'] = pandas.Series([min(draft['CORRDATE_fau'][i], 
                                           draft['CORRDATE_act'][i]) for i 
                                           in draft.index])
    draft['WUC'] = draft['WUC_fau']
    draft = draft.drop(['CORRDATE_fau', 'CORRDATE_act',
                        'WUC_fau', 'WUC_act'], axis=1)
    draft['EVENT_DATE'] = draft['FAULTDAT']
    draft['FAULTNO'] = draft['FAULTNO'].map(int)
    return draft

def vmep_faultnos_to_ints(num):
    if isinstance(num, str):
        return (int(num) if num.isdigit() else None)
    elif type(num) is float:
        return int(num)
    elif type(num) is int:
        return num
    return None

def ascii_to_df():
    fauRecords = list()
    actRecords = list()
    up = extract.extract_data(DEF.__ascii_base__, 'FAU', fauRecords)
    up += extract.extract_data(DEF.__ascii_base__, 'ACT', actRecords)
    
    fauRecords = clean.getRecords(fauRecords)
    actRecords = clean.getRecords(actRecords)
    
    fauRecords = clean.removeDuplicateRecords(fauRecords)
    actRecords = clean.removeDuplicateRecords(actRecords)
    
    fauRecords = clean.removeBlankNarrEvent(fauRecords)
    actRecords = clean.removeBlankNarrEvent(actRecords)
    
    fauRecords = clean.removeDuplicateIds(fauRecords)
    actRecords = clean.removeDuplicateIds(actRecords)
    
    fauDF = toDataFrame(fauRecords, DEF.__ascii_FAU_fields__)
    actDF = toDataFrame(actRecords, DEF.__ascii_ACT_fields__)
    
    return merge_ascii(fauDF, actDF)

def ascii_plus_vmep():
    return pandas.concat(
        [vmep_to_df(), ascii_to_df()]
        )#.sort(['EI_ID', 'EVENT_DATE', 'FAULTNO'],
                #inplace=True, 
          #      ascending=[1,0,0])

def vmep_to_df():
    xl = pandas.ExcelFile(DEF.__latest_vmep__)
    vmep = xl.parse(DEF.__vmep_sheet_name__, index_col=None, na_values='')
#    vmep['FAULTNO'] = vmep['FAULTNO'].map(vmep_faultnos_to_ints)
    vmep['EI_ID'] = vmep['UNIT_ID'].map(clean.uid_to_eid)
    vmep = vmep.drop('UNIT_ID', axis=1)
    return vmep

def dash13_to_df():
    xl = pandas.ExcelFile(DEF.__dash13_filename__)
    d13 = xl.parse(DEF.__dash13_sheet_name__, index_col=None, na_values='')
    d13['EI_ID'] = d13['UNIT_ID']
    d13 = d13.drop('UNIT_ID', axis=1)
    return d13

id_cols = ['FAULTDAT', 'FAULTNO', 'EI_ID']    
def merge_ascii_vmep(asciiDF, vmepDF):    
    return pandas.merge(asciiDF, vmepDF, 
                        on=id_cols,
                        how='outer', 
                        suffixes=('_ascii', '_vmep'))
