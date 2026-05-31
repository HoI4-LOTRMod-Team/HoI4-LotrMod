
from state import *
from definitioncsv import *
import csv
import os

# This is a bonus script that uses some of nudge2's dependencies but isn't connected. Can be removed.

states = get_all_states()
candidates = []

prov_count_dict = {}


for st in states:
    if not st.is_impassable: # ignore impassable states
        candidates.append(st)
        prov_count_dict[st.state_id] = 0


def count_prov(prov):
    for st in candidates:
        if prov in st.province_list:
            prov_count_dict[st.state_id] += 1
            return


provs = get_definition_csv()

for p in provs:
    if p[6] == 'forest' or p[6] == 'jungle':
        count_prov(int(p[0]))


for st in candidates:
    if prov_count_dict[st.state_id] >= len(st.province_list) * 0.6:
        #print(f"State {st.state_id} ({st.filepath}) has {prov_count_dict[st.state_id] / len(st.province_list)} forest/jungle provinces.")
        print(str(st.state_id))