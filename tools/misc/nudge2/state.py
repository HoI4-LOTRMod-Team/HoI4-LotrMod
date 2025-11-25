from pdx_parser import *
from pathlib import Path


STATES_DIR = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\history\states'
STRAT_REGIONS_DIR = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\strategicregions'


class State:
    pObj = None
    province_list = []
    state_id = -1

    def __init__(self, file):
        self.pObj = ParseListFromFile_asPObj(file).Get("state")
        self.state_id = int(self.pObj.GetVal("id"))
        self.province_list = []
        provs = self.pObj.Get("provinces").value
        for prov in provs:
            self.province_list.append(int(prov.value))


def get_all_states():
    states = []

    mydir = Path(STATES_DIR)
    for filename in mydir.glob('*.txt'):
        states.append(State(filename))

    return states



class StratRegion:
    pObj = None
    province_list = []
    region_id = -1

    def __init__(self, file):
        self.pObj = ParseListFromFile_asPObj(file).Get("strategic_region")
        self.region_id = int(self.pObj.GetVal("id"))
        self.province_list = []
        provs = self.pObj.Get("provinces").value
        for prov in provs:
            self.province_list.append(int(prov.value))


def get_all_stratregion():
    regions = []

    mydir = Path(STRAT_REGIONS_DIR)
    for filename in mydir.glob('*.txt'):
        regions.append(StratRegion(filename))

    return regions









