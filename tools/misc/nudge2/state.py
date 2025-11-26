from pdx_parser import *
from pathlib import Path
from locfile import *

BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() # Points at the lotr/ directory
STATES_DIR = BASE_PATH / "history/states"
STATES_LOC_DIR = BASE_PATH / "localisation/english/state_names_l_english.yml"
STRAT_REGIONS_DIR = BASE_PATH / "map/strategicregions"


class State:
    pObj = None
    province_list = []
    state_id = -1
    is_impassable = False
    filepath = ""

    def __init__(self, file):
        self.pObj = ParseListFromFile_asPObj(file).Get("state")
        self.state_id = int(self.pObj.GetVal("id"))
        self.filepath = file
        self.province_list = []
        self.is_impassable = self.pObj.Has("impassable") and self.pObj.GetVal("impassable") == "yes"
        provs = self.pObj.Get("provinces").value
        for prov in provs:
            self.province_list.append(int(prov.value))

    def apply_province_changes(self):
        self.pObj.Get("provinces").value = ParseTokenList(" ".join([str(p) for p in self.province_list]), parent=self.pObj.Get("provinces"))

    def save_to_file(self):
        SaveObjToFile(self.pObj, self.filepath)


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
		owner = MOR
		buildings = {
			infrastructure = 1
		}
		add_core_of = MOR
	}

	provinces = {
		
	}
	manpower = 1000
	buildings_max_level_factor = 1.000
	state_category = wasteland
	local_supplies=1.000
}
"""


def create_new_state(provinces, state_name):
    all_states = get_all_states()

    # sort provinces array
    provinces.sort()

    # figure out what the highest state id is to get new id
    new_state_id = -999
    for st in all_states:
        if st.state_id > new_state_id: new_state_id = st.state_id
    new_state_id += 1

    # create empty template
    state_text = STATE_TEMPLATE.replace("$TOKEN_ID$", str(new_state_id))

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
    loc.save()

    # TODO: fix strategic regions


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
        if st.pObj.Has("history") and st.pObj.Get("history").Has("victory_points"):
            for vp in st.pObj.Get("history").GetAll("victory_points").value:
                if int(vp.value[0].value) not in st.province_list:
                    vps.append(vp)
                    st.pObj.Get("history").value.remove(vp)

    # fix buildings
    buildings = []
    for st in changed_states:
        if st.pObj.Has("history") and st.pObj.Get("history").Has("buildings"):
            for bld in st.pObj.Get("history").Get("buildings").value:
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









