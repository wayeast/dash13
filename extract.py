"""
Routines for extracting data from unworked ASCII data files
"""

import re, os
from . import defaults as DEF

##########################################################
# regular expressions, etc. to catch those lines we don't
#   care about and those we do
#
DATELINE = re.compile('^[0-9]{1,2} [A-Z]{3} [0-9]{4} *([0-9]{2}:){2}[0-9]{2}$')
STATUSLINE = re.compile('^AIRCRAFT STATUS REPORT - CLOSED FAULTS$')
REDXLINE = re.compile('^\* = RED X$')
CIRCLELINE = re.compile('^A/C   +MDS    +A/C HRS PHASE  +\+ = CIRCLE RED X$')
STFAULTLINE = re.compile('^ST FAULT DT #')
FIELDLINE = re.compile('^Field #   Name')
AWAAMLINE = re.compile('.*AWAAM.*')
TOTRECORDSLINE = re.compile('^TOTAL RECORDS PRINTED')
TOTPAGESLINE = re.compile('^TOTAL PAGES PRINTED')
TOTFIELDSLINE = re.compile('^TOTAL FIELDS USED')
ELAPSEDTIMELINE = re.compile('^ELAPSED TIME FOR REPORT')
SUMMARYLINE = re.compile('^SUMMARY OF ADHOC REPORT')
DASHLINE = re.compile('^-{50,}')
STARLINE = re.compile('^\*{50,}')
PAGENUMLINE = re.compile('^[0-9]+$')
PAGENUMRANGE = 1000  # assume a lone number <= 1000 is a page number

def simplify(s):
    """Routine to identify those bothersome ascii art 'closed' lines"""
    ret = ''
    current = ''
    for c in s:
        if not c.isspace() and c != current:
            ret += c
            current = c
    return ret

def likelyPageNo(s):
    if (PAGENUMLINE.match(s) and
        int(s) <= PAGENUMRANGE):
        return True
    return False
    
def interesting(s):
    """Determine if a line is worth trying to process."""
    if not s: return False
    elif DATELINE.match(s): return False
    elif STATUSLINE.match(s): return False
    elif REDXLINE.match(s): return False
    elif CIRCLELINE.match(s): return False
    elif STFAULTLINE.match(s): return False
    elif FIELDLINE.match(s): return False
    elif AWAAMLINE.match(s): return False
    elif TOTRECORDSLINE.match(s): return False
    elif TOTPAGESLINE.match(s): return False
    elif TOTFIELDSLINE.match(s): return False
    elif ELAPSEDTIMELINE.match(s): return False
    elif SUMMARYLINE.match(s): return False
    elif DASHLINE.match(s): return False
    elif STARLINE.match(s): return False
    elif simplify(s) == 'CLOSED': return False
    elif likelyPageNo(s):
        return False
    return True

#
############################################################


############################################################
# Helper functions for handleline
#
def tooFewValues(line):
    return len(line.split()) <= 2
def looksLikeDate(s):
    return len(s) == 8 and s.isdigit()
def isJunkU(s):
    """
    Some records have an extraneous 'U' or other character that
    Carlyle says is unimportant.
    """
    return (s in ['U', 'UN', '\\', '.'])
def looksLikeSysCode(s):
    return s in 'AWEO'
def looksLikeModel(s):
    return s[:2] in ['AH', 'UH', 'CH']
def looksLikeStatus(s):
    return s in '-*CNXB+/'

def firstToken(s):
    return s.split(None, 1)[0]
def secondToken(s):
    return s.split(None, 2)[1]
def thirdToken(s):
    return s.split(None, 3)[2]
def fourthToken(s):
    return s.split(None, 4)[3]
def fifthToken(s):
    return s.split(None, 5)[4]
def sixthToken(s):
    return s.split(None, 6)[5]
def seventhToken(s):
    return s.split(None, 7)[6]
def eighthToken(s):
    return s.split(None, 8)[7]
def noNarrField(l):
    """Indexing specific to pre-recordId entries."""
    return len(l) < 9

def check(entry):
    # some basic checks for line integrity
    if not hasRightNumberFields(entry):
        #print entry
        return False
    if (corrDateField(entry) and
        not looksLikeDate(corrDateField(entry))):
        #print entry
        return False
    if not looksLikeSysCode(sysCodeField(entry)):
        #print entry
        return False
    if not looksLikeModel(modelField(entry)):
        #print entry
        return False
    if not looksLikeDate(faultDateField(entry)):
        #print entry
        return False
    if (statusField(entry) and
        not looksLikeStatus(statusField(entry))):
        #print entry
        return False
    return True

def hasRightNumberFields(entry):
    return len(entry) == 9
def corrDateField(entry):
    return entry[0]
def sysCodeField(entry):
    return entry[2]
def modelField(entry):
    return entry[3]
def faultDateField(entry):
    return entry[5]
def statusField(entry):
    return entry[7]
#
#############################################################


def fauact_filter(filenames, flag):
    """
    Current filter for treating 'FAUACT' files as 'ACT' files
    Called in extract_data to filter filenames.
    """
    if flag == 'ACT':
        return [f for f in filenames if flag in f]
    return [f for f in filenames if flag in f and not 'ACT' in f]
    
def extract_data(startpath, FLAG, out):
    """
    Walk through subdirectory at startpath looking for files with (possible)
    data lines.  With 'out' as filename, write extracted data to out as csv,
    separated by constants.__ascii_csv_delim__.  With 'out' as list handle,
    append extracted data as list to 'out.'
    
    @type  startpath: str
    @param startpath: top of subdirectory to be searched
    @type  FLAG: str
    @param FLAG: substring for selecting searched files (should be 'FAU' or
                 'ACT')
    @type  out: str or list
    @param out: as string, filename of csv file to which extracted data should
                be written.  As list, list to which extracted data, as a list
                of values, should be appended
    @rtype:   list
    @return:  list of data strings found to be interesting but which could not
              be processed by extract_data
    """
    weirdos = list()
    try:
        dataout = open(out, 'w')
    except TypeError:
        dataout = out

    for root, dirs, files in os.walk(startpath):
        for f in fauact_filter(files, FLAG):
            with open(os.path.join(root, f), 'r') as read:
                # contortions here with alternating lines are to handle narrative
                # entries in FAU files that are broken into two lines.  Some
                # of these breaks happen around page breaks in the files
                buf = read.readline().strip()
                nextline = read.readline()
                lineno = 1  # line number in buffer
                while nextline:
                    if interesting(buf):
                        if interesting(nextline.strip()):
                            # handle case where narr split b/w lines
                            buf += nextline.strip()
                            nextline = read.readline()
                            lineno += 1
                        elif likelyPageNo(nextline.strip()):
                            # handle case where narr split b/w pages
                            while (nextline and 
                                   not interesting(nextline.strip())):
                                nextline = read.readline()
                                lineno += 1
                            if nextline and len(nextline.split()) <= 4:  # number found by experimentation
                                buf += nextline.strip()
                                nextline = read.readline()
                                lineno += 1
                        # write out what's in buf
                        w = handleline(buf, dataout, 
                                       os.path.join(root, f), lineno)
                        if w is not None:
                            weirdos.append((w, os.path.join(root, f), lineno))
                    # check before assigning EOF to buf
                    if nextline:
                        buf = nextline.strip()
                        lineno += 1
                        nextline = read.readline()
                # don't forget last line in buffer...
                if interesting(buf):
                    w = handleline(buf, dataout, os.path.join(root, f), lineno)
                    if w is not None:
                        weirdos.append((w, os.path.join(root, f), lineno))

    try:
        dataout.close()
    except AttributeError:
        pass

    return weirdos

def handleline(line, out, filename, lineno):
    """Write csv line to file <out> or append list of values to list <out>."""
    if tooFewValues(line):
        return line
    l = list()
    if looksLikeDate(firstToken(line)):
        if isJunkU(thirdToken(line)):
            l = line.split(None, 3)
            l.pop(2)
            line = ' '.join(l)
        if looksLikeSysCode(fourthToken(line)): # wuc code looks split
            l = line.split(None, 9)
            l[1] += '-' + l[2]
            l.pop(2)
            line = ' '.join(l)
        if looksLikeModel(secondToken(line)):  # no wuc, no sys code
            if not looksLikeStatus(sixthToken(line)):  # missing status value
                l = line.split(None, 5)
                l.insert(1, '')
                l.insert(2, '')
                l.insert(7, '')
            else:
                l.insert(1, '')
                l.insert(2, '')
        elif looksLikeSysCode(thirdToken(line)): # something probly exists in wuc code
            l = line.split(None, 8)
        else: # insert null value for wuc code
            l = line.split(None, 7)
            l.insert(1, '')
    else:  # date completed not found
        if isJunkU(secondToken(line)):
            l = line.split(None, 2)
            l.pop(1)
            line = ' '.join(l)
        if looksLikeSysCode(thirdToken(line)): # wuc code looks split
            l = line.split(None, 8)
            l[0] += '-' + l[1]
            l.pop(1)
            line = ' '.join(l)
        if looksLikeSysCode(secondToken(line)): # something probly exists for wuc code
            l = line.split(None, 7)
            l.insert(0, '')            # insert null value for date completed
        else:
            l = line.split(None, 6)
            l.insert(0, '') #insert null value for date completed
            l.insert(1, '') #insert null value for wuc code

    if noNarrField(l):
        l.append('')

    # line cleaned up as much as can be, now check, polish, write
    if check(l):
        l.append(filename)
        l.append(str(lineno))
        try:
            out.write(DEF.__ascii_csv_delim__.join(l) + '\n')
            return None
        except AttributeError:
            pass
        try:
            out.append(l)
            return None
        except AttributeError:
            print "From handleline, cannot output data to %s" % out
            raise
    return line

#######################################################################
# definitions for examining FAUACT files
#def is_fauact(name):
#    return (name.find('FAU') >= 0 and
#            name.find('ACT') >= 0)
#
#def extract_data_nofauact(startpath, FLAG, out):
#    """
#    Walk through subdirectory at startpath looking for (possible)
#    data lines.  Write extracted data to fout as csv, separated by
#    constants.__ascii_csv_delim__.
#    """
#    weirdos = list()
#    try:
#        dataout = open(out, 'w')
#    except TypeError:
#        dataout = out
#
#    for root, dirs, files in os.walk(startpath):
#        for f in [f for f in files if  # select files with FLAG but not FAUACT
#                  f.find(FLAG) >= 0 and
#                  not is_fauact(f)]:
#            with open(os.path.join(root, f), 'r') as read:
#                # contortions here with alternating lines are to handle narrative
#                # entries in FAU files that are broken into two lines.  Some
#                # of these breaks happen around page breaks in the files
#                buf = read.readline().strip()
#                nextline = read.readline()
#                lineno = 1  # line number in buffer
#                while nextline:
#                    if interesting(buf):
#                        if interesting(nextline.strip()):
#                            # handle case where narr split b/w lines
#                            buf += nextline.strip()
#                            nextline = read.readline()
#                            lineno += 1
#                        elif likelyPageNo(nextline.strip()):
#                            # handle case where narr split b/w pages
#                            while nextline and not interesting(nextline.strip()):
#                                nextline = read.readline()
#                                lineno += 1
#                            if nextline and len(nextline.split()) <= 4:  # number found by experimentation
#                                buf += nextline.strip()
#                                nextline = read.readline()
#                                lineno += 1
#                        # write out what's in buf
#                        w = handleline(buf, dataout, os.path.join(root, f), lineno)
#                        if w is not None:
#                            weirdos.append((w, os.path.join(root, f), lineno))
#                    # check before assigning EOF to buf
#                    if nextline:
#                        buf = nextline.strip()
#                        lineno += 1
#                        nextline = read.readline()
#                # don't forget last line in buffer...
#                if interesting(buf):
#                    w = handleline(buf, dataout, os.path.join(root, f), lineno)
#                    if w is not None:
#                        weirdos.append((w, os.path.join(root, f), lineno))
#
#    try:
#        dataout.close()
#    except AttributeError:
#        pass
#
#    return weirdos
#
#def extract_data_fauact(startpath, out):
#    """
#    Walk through subdirectory at startpath looking for (possible)
#    data lines.  Write extracted data to fout as csv, separated by
#    constants.__ascii_csv_delim__.
#    """
#    weirdos = list()
#    try:
#        dataout = open(out, 'w')
#    except TypeError:
#        dataout = out
#
#    for root, dirs, files in os.walk(startpath):
#        for f in [f for f in files if  # select files with FLAG but not FAUACT
#                  is_fauact(f)]:
#            with open(os.path.join(root, f), 'r') as read:
#                # contortions here with alternating lines are to handle narrative
#                # entries in FAU files that are broken into two lines.  Some
#                # of these breaks happen around page breaks in the files
#                buf = read.readline().strip()
#                nextline = read.readline()
#                lineno = 1  # line number in buffer
#                while nextline:
#                    if interesting(buf):
#                        if interesting(nextline.strip()):
#                            # handle case where narr split b/w lines
#                            buf += nextline.strip()
#                            nextline = read.readline()
#                            lineno += 1
#                        elif likelyPageNo(nextline.strip()):
#                            # handle case where narr split b/w pages
#                            while nextline and not interesting(nextline.strip()):
#                                nextline = read.readline()
#                                lineno += 1
#                            if nextline and len(nextline.split()) <= 4:  # number found by experimentation
#                                buf += nextline.strip()
#                                nextline = read.readline()
#                                lineno += 1
#                        # write out what's in buf
#                        w = handleline(buf, dataout, os.path.join(root, f), lineno)
#                        if w is not None:
#                            weirdos.append((w, os.path.join(root, f), lineno))
#                    # check before assigning EOF to buf
#                    if nextline:
#                        buf = nextline.strip()
#                        lineno += 1
#                        nextline = read.readline()
#                # don't forget last line in buffer...
#                if interesting(buf):
#                    w = handleline(buf, dataout, os.path.join(root, f), lineno)
#                    if w is not None:
#                        weirdos.append((w, os.path.join(root, f), lineno))
#
#    try:
#        dataout.close()
#    except AttributeError:
#        pass
#
#    return weirdos
#
#def extract_all_dash13(start=DEF.__ascii_base__,
#                       act_out=DEF.__fresh_act_csv__,
#                       fau_out=DEF.__fresh_fau_csv__,
#                       act_errors=None,
#                       fau_errors=None):
#    """
#    Extract all data from ACT and FAU files in ASCII_BASE, return
#    lines that look interesting but can't be processed.    
#    """
#    unprocessables = list()
#    for flag in ['ACT', 'FAU']:
#        dbf = (fau_out if flag == 'FAU' else
#               act_out)
#        writeout = (fau_errors if flag == 'FAU' else
#                    act_errors)
#        unprocessables += extract_data(start,
#                                       flag,
#                                       dbf,
#                                       writeout)
#    return unprocessables

