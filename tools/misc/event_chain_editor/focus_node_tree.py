import json
import os
from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj, SaveObjValueToFile

from core import *

from focus_node import FocusNode

from locfile import LocFile


class FocusNodeTree:

    focuses = []

    fake_focuses = []

    root_pobj = None

    graph = None

    locfile = None

    focusfilepath = None

    namespace_id = ""
    
    # Hard-coded name for the positions file alongside the script
    POSITIONS_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_positions.json")

    def get_focus_node_by_name(self, name):
        for focus in self.focuses:
            if focus.focus_id == name:
                return focus
        return None
    
    def get_fake_focus_node_by_name(self, name):
        for focus in self.fake_focuses:
            if focus.focus_id == name:
                return focus
        return None
    
    def save_focus_tree(self, filepath, locfilepath):
        # 1. Save the actual PObj data
        SaveObjValueToFile(self.root_pobj, filepath)
        self.locfile.save(locfilepath)

        # 2. Handle Node Positions
        try:
            # Load existing cache first
            cache = {}
            if os.path.exists(self.POSITIONS_CACHE_FILE):
                with open(self.POSITIONS_CACHE_FILE, 'r') as f:
                    try:
                        cache = json.load(f)
                    except json.JSONDecodeError:
                        cache = {} 

            # Get the current filename
            current_filename = os.path.basename(filepath)

            # Update cache with current positions
            for node in self.graph.all_nodes():
                if hasattr(node, 'focus_id'):
                    key = f"{current_filename}::{node.focus_id}"
                    # Convert pos to list to ensure JSON serializability
                    cache[key] = list(node.pos())

            # 3. Custom Write: formatted for one entry per line
            with open(self.POSITIONS_CACHE_FILE, 'w') as f:
                f.write("{\n")
                
                # Sort keys so the file doesn't shuffle randomly every save
                sorted_keys = sorted(cache.keys())
                
                for i, key in enumerate(sorted_keys):
                    # json.dumps ensures strings are escaped properly (e.g. if filename has spaces)
                    line = f'    {json.dumps(key)}: {json.dumps(cache[key])}'
                    
                    # Add a comma to all lines except the very last one
                    if i < len(sorted_keys) - 1:
                        line += ","
                    
                    f.write(line + "\n")
                
                f.write("}")
                
            print(f"Node positions saved to {self.POSITIONS_CACHE_FILE}")

        except Exception as e:
            print(f"Failed to save node positions: {e}")

    def load_positions(self):
        """
        Loads positions from the hard-coded JSON file and applies them 
        to nodes that match the current filename and node ID.
        """
        if not os.path.exists(self.POSITIONS_CACHE_FILE):
            return

        try:
            with open(self.POSITIONS_CACHE_FILE, 'r') as f:
                cache = json.load(f)

            current_filename = os.path.basename(self.focusfilepath)


            # Go through all nodes currently in the graph
            for node in self.graph.all_nodes():
                if hasattr(node, 'focus_id'):
                    key = f"{current_filename}::{node.focus_id}"
                    
                    if key in cache:
                        x, y = cache[key]
                        node.set_pos(x, y)
                        print(f"Loaded position for {node.focus_id}: ({x}, {y})")

        except Exception as e:
            print(f"Failed to load node positions: {e}")
    
    def __init__(self, graph, filepath, locfilepath):
        # Reset lists to ensure clean state on new init
        self.focuses = []
        self.fake_focuses = []

        self.focusfilepath = filepath

        self.graph = graph

        self.locfile = LocFile(locfilepath)

        focus_menu = graph.get_context_menu('graph').add_menu('Focus Tree')
        focus_menu.add_command('Save Focus Tree', lambda: self.save_focus_tree(filepath, locfilepath), 'Ctrl+S')

        self.root_pobj = ParseListFromFile_asPObj(filepath)

        self.namespace_id = self.root_pobj.GetVal("add_namespace")

        focuses_pobjs = self.root_pobj.GetAll("country_event").value

        # Create a node in the graph for each focus and set the respective values
        for focus in focuses_pobjs:
            focus_1 = graph.create_node('nodes.basic.FocusNode')
            focus_1.init(focus, self)

        # post-init function
        for focus in self.focuses:
            focus.post_init()

        # activate
        for focus in self.focuses:
            focus.activate()

        # Load positions after nodes are created and initialized
        #self.load_positions()