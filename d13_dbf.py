# -*- coding: utf-8 -*-
"""
Created on Sat Feb 01 16:22:14 2014

@author: Huston Bokinsky
"""

import xml.etree.ElementTree as et
import pandas

import dash13.defaults as DEF


def csvToDataFrame():
    dicts = list()
    with open(DEF.__dash13_csv__, 'r') as data:
        keys = data.readline().split(DEF.__ascii_csv_delim__)
        keys = [k.strip() for k in keys]
        print keys, '\n\n'
        for lineno, line in enumerate(data, 2):
            values = line.split(DEF.__ascii_csv_delim__)
            values = [v.strip() for v in values]
            temp = dict(zip(keys, values))
            #print temp['FAULTDAT'], temp['FAULTNO'], temp['UNIT_ID'], temp['SYS_CODE']
            try:
                temp['REC_ID'] = '_'.join([ temp['FAULTDAT'],
                                        temp['FAULTNO'],
                                        temp['UNIT_ID'],
                                        temp['SYS_CODE']
                                      ])
            except KeyError:
                print lineno, temp
                raise
            dicts.append(temp)
    return pandas.DataFrame(dicts)


def xmlToDataFrame():
    dicts = list()
    tree = et.parse(DEF.__dash13_xml__)
    root = tree.getroot()
    for record in root:
        rec = dict.fromkeys(DEF.__dash13_fields__, '')
        for field in record:
            rec[field.tag.strip()] = field.text
        rec['REC_ID'] = '_'.join([ rec['FAULTDAT'],
                                   rec['FAULTNO'],
                                   rec['UNIT_ID'],
                                   rec['SYS_CODE']
                                 ])
        #index = rec.pop('REC_ID')
        #dicts[index] = rec
        dicts.append(rec)
    #return pandas.DataFrame.from_dict(dicts, orient='index')
    return pandas.DataFrame(dicts)
