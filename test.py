import sys
sys.path.append("D:\\IBM")
import ascii


fauRecords = list()
actRecords = list()
start = ascii.defaults.__ascii_base__

##################################################################
## Extract data from raw FAU and ACT files and merge into
##   pandas.DataFrame
unprocessables = ascii.extract_data(start, 'FAU', fauRecords)
unprocessables += ascii.extract_data(start, 'ACT', actRecords)
# Check number of unprocessable lines
#print "Unable to extract %d lines" % len(unprocessables)

fauRecords = ascii.getRecords(fauRecords)
actRecords = ascii.getRecords(actRecords)

fauRecords = ascii.removeDuplicateRecords(fauRecords)
actRecords = ascii.removeDuplicateRecords(actRecords)

fauRecords = ascii.removeBlankNarrEvent(fauRecords)
actRecords = ascii.removeBlankNarrEvent(actRecords)

fauRecords = ascii.removeDuplicateIds(fauRecords)
actRecords = ascii.removeDuplicateIds(actRecords)

fauDF = ascii.toDataFrame(fauRecords)
actDF = ascii.toDataFrame(actRecords)

allAscii = ascii.merge(fauDF, actDF)
##
################################################################

##############################################################
# Create pandas.DataFrame from DASH13.DBF data
dash13 = ascii.dash13.xmlToDataFrame()
#
###############################################################



    ########################################################
    # for checking out FAUACT data
#    for flag in ['ACT', 'FAU']:
#        out = (extracted_fau_nofauact if flag == 'FAU' else
#               extracted_act_nofauact)
#        unprocessables += ascii.extract_data_nofauact(start,
#                                             flag,
#                                             out)
    #u = ascii.extract_data_fauact(start, extracted_fauact)
    
#    extracted_fau_nofauact = ascii.getRecords(extracted_fau_nofauact)
#    print "got %d records excluding fauact" % len(extracted_fau_nofauact)
#    extracted_fau_nofauact = ascii.removeDuplicateRecords(extracted_fau_nofauact)
#    print "yields %d non-duplicate records" % len(extracted_fau_nofauact)
#    extracted_fau_nofauact = ascii.removeBlankNarrEvent(extracted_fau_nofauact)
#    extracted_fau_nofauact = ascii.removeDuplicateIds(extracted_fau_nofauact,
#                                                      priority='byEventDate',
#                                                      check=True)
#
#    extracted_act_nofauact = ascii.getRecords(extracted_act_nofauact)
#    extracted_act_nofauact = ascii.removeDuplicateRecords(extracted_act_nofauact)

##    extracted_fauact = ascii.getRecords(extracted_fauact)
##    extracted_fauact = ascii.removeDuplicateRecords(extracted_fauact)
##    
##    neither= [rec.recID for rec in
##            extracted_fauact if
##            rec.recId not in [r.recId for r in extracted_fau_nofauact] and
##            rec.recId not in [r.recId for r in extracted_act_nofauact]
##            ]
##    act = [rec.recID for rec in
##            extracted_fauact if
##            rec.recId not in [r.recId for r in extracted_act_nofauact]
##           ]
##    fau = [rec.recID for rec in
##            extracted_fauact if
##            rec.recId not in [r.recId for r in extracted_fau_nofauact]
##           ]
##    print "fauact.recIds in neither fau nor act: %d \n\
##fauact.recIds not in act: %d \n\
##fauact.recIds not in fau: %d" % (len(neither), len(act), len(fau))
    #
    ##################################################################
            
    ##################################################################
    # test ascii data extractor...
##    print "Testing writing to lists..."
##    for flag in ['ACT', 'FAU']:
##        start = ascii.defaults.__ascii_base__
##        out = (extracted_fau if flag == 'FAU' else
##               extracted_act)
##        unprocessables += ascii.extract_data(start,
##                                             flag,
##                                             out)
##    print "unable to process %d lines from ascii files (u)" % len(unprocessables)
##    print "extracted %d lines from fau files" % len(extracted_fau)
##    print "extracted %d lines from act files" % len(extracted_act)
##
##    print "\nTesting writing to files..."
##    unprocessables = list()
##    for flag in ['ACT', 'FAU']:
##        start = ascii.defaults.__ascii_base__
##        out = (ascii.defaults.__fresh_fau_csv__ if flag == 'FAU' else
##               ascii.defaults.__fresh_act_csv__)
##        unprocessables += ascii.extract_data(start,
##                                             flag,
##                                             out)
##    print "unable to process %d lines from ascii files (u)" % len(unprocessables)
    #
    ##################################################################


    
#    recs = ascii.getRecords(ascii.defaults.__fresh_fau_csv__)  # return list of records
#    print "created %d records from extracted data (recs)" % len(recs)
#    #for rec in recs[:10]: print rec.to_csv()
#
#    rset = ascii.removeDuplicateRecords(recs)
#    print "yielded %d records after removing duplicate records (rset)" % len(rset)
#    #for rec in list(rset)[:10]: print rec.to_csv()
#
#    rcom = ascii.removeBlankNarrEvent(rset)
#    print "reduced to %d records after removing blank narrs and events (rcom)" % len(rcom)
#    #for rec in rcom[:10]: print rec.to_csv()
#
#    rniq = ascii.removeDuplicateIds(rcom, priority='byEventDate', check=True)
#    print "reduced to %d records after removing duplicate ids (rniq)" % len(rniq)
#
#    rsor = ascii.sortById(rniq)