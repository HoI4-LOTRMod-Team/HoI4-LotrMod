from pdx_parser import *
from pathlib import Path
from locfile import *

BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() # Points at the lotr/ directory
STATES_DIR = BASE_PATH / "history/states"
STATES_LOC_DIR = BASE_PATH / "localisation/english/state_names_l_english.yml"
REGIONS_LOC_DIR = BASE_PATH / "localisation/english/strategic_region_names_l_english.yml"
STRAT_REGIONS_DIR = BASE_PATH / "map/strategicregions"


class State:
    pObj = None
    province_list = []
    state_id = -1
    is_impassable = False
    filepath = ""
    owner = ""

    def __init__(self, file):
        self.pObj = ParseListFromFile_asPObj(file).Get("state")
        self.state_id = int(self.pObj.GetVal("id"))
        self.filepath = file
        self.province_list = []
        self.is_impassable = self.pObj.Has("impassable") and self.pObj.GetVal("impassable") == "yes"
        provs = self.pObj.Get("provinces").value
        for prov in provs:
            self.province_list.append(int(prov.value))

        if self.pObj.Has("history") and self.pObj.Get("history").Has("owner"):
            self.owner = str(self.pObj.Get("history").GetVal("owner"))

    def apply_province_changes(self):
        self.pObj.Get("provinces").value = ParseTokenList(" ".join([str(p) for p in self.province_list]), parent=self.pObj.Get("provinces"))

    def save_to_file(self):
        SaveObjToFile(self.pObj, self.filepath)

    def get_vp_list(self):
        if self.pObj.Has("history") and self.pObj.Get("history").Has("victory_points"):
            return self.pObj.Get("history").GetAll("victory_points").value
        return []
    
    def get_bld_list(self):
        if self.pObj.Has("history") and self.pObj.Get("history").Has("buildings"):
            return self.pObj.Get("history").Get("buildings").value
        return []


def get_all_states():
    states = []

    mydir = Path(STATES_DIR)
    for filename in mydir.glob('*.txt'):
        states.append(State(filename))

    return states


STATE_TEMPLATE = """
state = {
	id=$TOKEN_ID$
	name="STATE_$TOKEN_ID$"
	resources = {
		
	}

	history={
		owner = $TOKEN_OWNER$
		buildings = {
			infrastructure = 1
		}
		add_core_of = $TOKEN_OWNER$
	}

	provinces = {
		
	}
	manpower = 1000
	buildings_max_level_factor = 1.000
	state_category = wasteland
	local_supplies=1.000
}
"""

REGION_TEMPLATE = """
strategic_region = {
	id=$TOKEN_ID$
	name="STRATEGICREGION_$TOKEN_ID$"

	provinces = {
		
	}
}
"""


def create_new_state(provinces, state_name, state_owner_tag):
    all_states = get_all_states()

    # sort provinces array
    provinces.sort()

    # figure out what the highest state id is to get new id
    new_state_id = -999
    for st in all_states:
        if st.state_id > new_state_id: new_state_id = st.state_id
    new_state_id += 1

    # create empty template
    state_text = STATE_TEMPLATE.replace("$TOKEN_ID$", str(new_state_id)).replace("$TOKEN_OWNER$", state_owner_tag)

    # save to file
    dir = STATES_DIR / (str(new_state_id) + "-" + state_name + ".txt")
    with open(dir, "w") as f:
        f.write(state_text)

    # transfer provinces to new state
    new_state = State(dir)
    transfer_provinces_to_state(provinces, new_state.state_id)

    # Add localization entry
    loc = LocFile(STATES_LOC_DIR)
    loc.add("STATE_"+str(new_state_id), state_name)
    loc.save(STATES_LOC_DIR)


def create_new_strategicregion(provinces, region_name):
    all_regions = get_all_stratregion()

    # sort provinces array
    provinces.sort()

    # figure out what the highest region id is to get new id
    new_region_id = -999
    for st in all_regions:
        if st.region_id > new_region_id: new_region_id = st.region_id
    new_region_id += 1

    # create empty template
    state_text = REGION_TEMPLATE.replace("$TOKEN_ID$", str(new_region_id))

    # save to file
    dir = STRAT_REGIONS_DIR / (str(new_region_id) + "-" + region_name + ".txt")
    with open(dir, "w") as f:
        f.write(state_text)

    # transfer provinces to new strategic region
    new_region = StratRegion(dir)
    transfer_provinces_to_strategicregion(provinces, new_region.region_id)

    # Add localization entry
    loc = LocFile(REGIONS_LOC_DIR)
    loc.add("STRATEGICREGION_"+str(new_region_id), region_name)
    loc.save(REGIONS_LOC_DIR)


def transfer_provinces_to_state(provinces, destination_state_id):
    all_states = get_all_states()

    target_state = None

    # Remove the transferred provinces from other states
    changed_states = []
    for st in all_states:
        if st.state_id != destination_state_id:
            for p in provinces:
                if p in st.province_list:
                    if st not in changed_states: changed_states.append(st)
                    st.province_list.remove(p)
            st.apply_province_changes()
        else:
            target_state = st

    # fix victory points
    vps = []
    for st in changed_states:
        for vp in st.get_vp_list():
            if int(vp.value[0].value) not in st.province_list:
                vps.append(vp)
                st.pObj.Get("history").value.remove(vp)

    # fix buildings
    buildings = []
    for st in changed_states:
        for bld in st.get_bld_list():
            if bld.id.isnumeric() and int(bld.id) not in st.province_list:
                buildings.append(bld)
                st.pObj.Get("history").Get("buildings").value.remove(bld)


    # save changed state files
    for st in changed_states:
        st.save_to_file()

    # transfer the provinces to the target state
    for p in provinces:
        if p not in target_state.province_list:
            target_state.province_list.append(p)
    target_state.province_list.sort()
    target_state.apply_province_changes()

    # transfer victory points and buildings
    for vp in vps:
        target_state.pObj.Get("history").Insert(str(vp))
    for bld in buildings:
        target_state.pObj.Get("history").Get("buildings").Insert(str(bld))
    target_state.save_to_file()

    # fix strat regions
    fix_strat_regions(target_state.province_list)


def transfer_provinces_to_strategicregion(provinces, destination_region_id):
    all_regions = get_all_stratregion()

    target_region = None

    # Remove the transferred provinces from other states
    changed_regions = []
    for st in all_regions:
        if st.region_id != destination_region_id:
            for p in provinces:
                if p in st.province_list:
                    if st not in changed_regions: changed_regions.append(st)
                    st.province_list.remove(p)
            st.apply_province_changes()
        else:
            target_region = st

    # save changed state files
    for st in changed_regions:
        st.save_to_file()

    # transfer the provinces to the target state
    for p in provinces:
        if p not in target_region.province_list:
            target_region.province_list.append(p)
    target_region.province_list.sort()
    target_region.apply_province_changes()
    target_region.save_to_file()



def fix_strat_regions(provinces_in_state):
    regions = get_all_stratregion()
    prov_set = set(provinces_in_state)

    # Find region with the most overlap on the changed provinces
    best_region = max(regions, key=lambda obj: len(prov_set.intersection(obj.province_list)))

    # transfer these provinces to that strat region
    transfer_provinces_to_strategicregion(provinces_in_state, best_region.region_id)





class StratRegion:
    pObj = None
    province_list = []
    region_id = -1
    filepath = ""

    def __init__(self, file):
        self.pObj = ParseListFromFile_asPObj(file).Get("strategic_region")
        self.region_id = int(self.pObj.GetVal("id"))
        self.province_list = []
        self.filepath = file
        provs = self.pObj.Get("provinces").value
        for prov in provs:
            self.province_list.append(int(prov.value))

    def apply_province_changes(self):
        self.pObj.Get("provinces").value = ParseTokenList(" ".join([str(p) for p in self.province_list]), parent=self.pObj.Get("provinces"))

    def save_to_file(self):
        SaveObjToFile(self.pObj, self.filepath)


def get_all_stratregion():
    regions = []

    mydir = Path(STRAT_REGIONS_DIR)
    for filename in mydir.glob('*.txt'):
        regions.append(StratRegion(filename))

    return regions






