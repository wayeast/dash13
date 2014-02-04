"""
Cull and clean up raw ASCII data.
"""


import ascii.defaults as DEF


############################################
# serial number scrub mappings and scrubber routine

_serno_uid_map = dict()  # serial no to uid map
with open(DEF.__serno_to_uid__, 'r') as f:
    for line in f:
        line = line.split()
        _serno_uid_map[line[0]] = line[2]

def serno_to_uid(serno):
    return (_serno_uid_map[serno] if
            serno in _serno_uid_map else
            serno)

_uid_eid_map = dict()  # uid to eid map
with open(DEF.__uid_to_ei__, 'r') as f:
    for line in f:
        line = line.split()
        _uid_eid_map[line[0]] = line[1]

def uid_to_eid(uid):
    return (_uid_eid_map[uid] if
            uid in _uid_eid_map else
            uid)

def scrub_serno(serno):
    return uid_to_eid(serno_to_uid(serno))
#
############################################


class Record(object):
    def __init__(self, l):
        if len(l) != 11:  # quick check
            raise RuntimeError("Cannot create record from list: %s" % str(l))
        
        l[4] = scrub_serno(l[4])
        self.values = tuple(l)

    @property
    def wholerec(self):
        """"wholerec is all values except filename and line no"""
        return self.values[:-2]

    @property
    def recId(self):
        return '_'.join([self.EVENT_DATE,
                         self.EVENT_NO,
                         self.EI_ID,
                         self.SYS_CODE
                         ])

    @property
    def CORR_DATE_TIME(self):
        return self.values[0]

    @property
    def WUC(self):
        return self.values[1]

    @property
    def SYS_CODE(self):
        return self.values[2]

    @property
    def MODEL(self):
        return self.values[3]

    @property
    def EI_ID(self):
        return self.values[4]

    @property
    def EVENT_DATE(self):
        return self.values[5]

    @property
    def EVENT_NO(self):
        return self.values[6]

    @property
    def STATUS(self):
        return self.values[7]

    @property
    def NARR(self):
        return self.values[8]

    def to_csv(self):
        values = list(self.values)
        values.insert(0, self.recId)
        return DEF.__ascii_csv_delim__.join(values)
    
    def __repr__(self):
        return str(self.wholerec)

    def __hash__(self):
        return hash(''.join(self.wholerec))

    def __eq__(self, other):
        return hash(self) == hash(other)
        #return ''.join(self.wholerec) == ''.join(other.wholerec)

    @property
    def sortableId(self):
        ''.join([self.EI_ID, self.EVENT_DATE, self.EVENT_NO])



#def recsToDict(rl):
#    """
#    Return a dict of recId : wholerec items from <rl>.
#    
#    @type  rl: list
#    @param rl: list of Records
#    @rtype: dict
#    @return: dict of recId : wholerec items.  Meant to be read into
#             pandas.DataFrame by DataFrame.from_dict()
#    """
#    return {r.recId : r.wholerec for r in rl}
    
def getRecords(fromloc):
    """
    Return list of Records from fromloc.
    
    @type  fromloc: str or list
    @param fromloc: location of extracted data to import into Record list
    @rtype:  list
    @return: extracted ascii data as list of Records
    """
    ret = list()
    try:
        fromfile = open(fromloc, 'r')
        ret = [Record(line.split(DEF.__ascii_csv_delim__)) for
               line in
               fromfile]
        fromfile.close()
    except TypeError:
        ret = [Record(valuelist) for valuelist in fromloc]

    return ret

def sortById(recList):
    """
    Sort recList by ei id, event date, event number.
    
    @type  recList: list
    @param recList: list of Records to be sorted
    @rtype: list
    @return: recList sorted by ei id, event date, event number
    """
    return sorted(recList, key=lambda rec : rec.sortableId)

def removeDuplicateRecords(rl):
    """
    Return list of unique Records from filename.

    @type  rl: list
    @param rl: list of Records
    @rtype: list
    @return: list of distinct Records.  Distinctness is measured by the
             amalgamation of all Record fields save filename and line number.
    """
    return list(set(rl))

def removeBlankNarrEvent(rl):
    """Remove records with blank CORR_DATE_TIME or NARR from rl."""
    return [r for r in rl if r.CORR_DATE_TIME and r.NARR]

from collections import defaultdict
def removeDuplicateIds(rl, priority='byEventDate', check=False):
    """
    Remove duplicate recordIds.
    
    @type  rl: list
    @param rl: list of Records
    @type  priority: str
    @param priority: indicates priority by which Records with same recordIds
                     should be culled.  May be either 'byEventDate' or
                     'byNarr'.  'byEventDate' is default.
    @type  check: boolean
    @param check: indicates whether to record discarded Records (True) or
                  not (False).  False is default.
    @rtype: list
    @return: list of Records with distinct recordIds.  Records are culled
             according to <priority>
    """
    if priority not in ['byNarr', 'byEventDate']:
        raise RuntimeError("removeDuplicateIds requires priority argument 'byNarr' or 'byEventDate'")

    ret = defaultdict(list)
    for record in rl:
        ret[record.recId].append(record)  # build dict from records by recordId
    thinLists(ret, priority, check)
    return ret.values()

#########################################################
# for testing
discarded_narrEvent = "D:\\IBM\\narrEvent_choices.txt"
narrEvent_text = """When removing duplicate recordIds, these decisions were made
by 1) length of narrative field, 2) latter eventDate

"""
discarded_eventNarr = "D:\\IBM\\eventNarr_choices.txt"
eventNarr_text = """When removing duplicate recordIds, these decisions were made
by 1) latter eventDate, 2) length of narrative field

"""
#
########################################################

def thinLists(d, priority, check):
    ###############################################################
    # some helper function definitions for cleanliness
    def recCmpNarr(rec1, rec2):
        diff = len(rec1.NARR) - len(rec2.NARR)
        return (int(rec1.EVENT_DATE) - int(rec2.EVENT_DATE) if
                not diff else diff)

    def recCmpEvent(rec1, rec2):
        diff = int(rec1.EVENT_DATE) - int(rec2.EVENT_DATE)
        return (diff if diff else
                len(rec1.NARR) - len(rec2.NARR))
    
    def sortRecs(rl, priority):
        return sorted(rl,
                      cmp=(recCmpNarr if priority == 'byNarr' else
                           recCmpEvent),
                      reverse=True)

    def topRec(rl, priority):
        return sortRecs(rl, priority)[0]

    def writeChoices(f, rl, priority):
        if len(rl) > 1:
            rl = sortRecs(rl, priority)
            if (priority == 'byNarr' and
                len(rl[0].NARR) == len(rl[1].NARR)):
                f.write("\nSelected:\n%s\n" %(str(rl[0])))
                f.write("Discarded:\n")
                for r in rl[1:]:
                    f.write(str(r) + '\n')
            elif (priority == 'byEventDate' and
                rl[0].EVENT_DATE == rl[1].EVENT_DATE):
                f.write("\nSelected:\n%s\n" %(str(rl[0])))
                f.write("Discarded:\n")
                for r in rl[1:]:
                    f.write(str(r) + '\n')
    #
    ###############################################################

    ###############################################################
    # if checking choices, we will need to write them to an appropriate file
    if check:
        fout = open(discarded_narrEvent if priority == "byNarr" else
                    discarded_eventNarr,
                    'w')
        fout.write(narrEvent_text if priority == "byNarr" else
                   eventNarr_text)
        
    ###############################################################
    # core of thinList function
    for key in d.keys():
        selected = topRec(d[key], priority)
        if check:
            writeChoices(fout, d[key], priority)
        d[key] = selected

    if check:
        fout.close()


    # end of thinLists function

