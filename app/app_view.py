'''
By using this source code, you acknowledge that this software in source code form remains a confidential information of AnyLog, Inc.,
and you shall not transfer it to any other party without AnyLog, Inc.'s prior written consent. You further acknowledge that all right,
title and interest in and to this source code, and any copies and/or derivatives thereof and all documentation, which describes
and/or composes such source code or any such derivatives, shall remain the sole and exclusive property of AnyLog, Inc.,
and you shall not edit, reverse engineer, copy, emulate, create derivatives of, compile or decompile or otherwise tamper or modify
this source code in any way, or allow others to do so. In the event of any such editing, reverse engineering, copying, emulation,
creation of derivative, compilation, decompilation, tampering or modification of this source code by you, or any of your affiliates (term
to be broadly interpreted) you or your such affiliates shall unconditionally assign and transfer any intellectual property created by any
such non-permitted act to AnyLog, Inc.
'''
from flask import url_for

import json

from config import Config


# ------------------------------------------------------------------------
# The process to load a JSON file that maintanins the GUI view of the data/metadata
# ------------------------------------------------------------------------

class gui():

    def __init__(self):
        self.gui_struct = None 
        self.base_menue = None
   # ------------------------------------------------------------------------
    # Load the JSON and set main structures
    # ------------------------------------------------------------------------
    def set_gui(self, file_name = None):

        if not file_name:
            file_name = Config.GUI_VIEW    # get from system variable
        
        self.gui_struct = load_json(file_name)

 
    # ------------------------------------------------------------------------
    # Set Menu names and links based on the JSON file
    # ------------------------------------------------------------------------
    def set_menue(self):
        if self.gui_struct and not self.base_menue:
            self.base_menue = []
            if isinstance(self.gui_struct, dict):
                if "gui" in self.gui_struct and "children" in self.gui_struct["gui"]:     # Root of JSON
                    self.create_base_menue(self.gui_struct["gui"]["children"])


    # ------------------------------------------------------------------------
    # Make the upper menue
    # ------------------------------------------------------------------------
    def create_base_menue(self, gui_list):

        if isinstance(gui_list,list):
            for entry in gui_list:
                if isinstance(entry, dict):
                    if "name" in entry:
                        text_name = entry["name"]
                        try:
                            url_link = url_for(text_name.lower())
                        except:
                            continue
                        self.base_menue.append((text_name, url_link))
                        if "children" in entry:
                           self.create_base_menue(entry["children"])

    # ------------------------------------------------------------------------
    # Return the user menue based on the JSON file
    # ------------------------------------------------------------------------
    def get_base_menu(self):
        return self.base_menue
# ------------------------------------------------------------------------
# The process to load a JSON file that maintanins the GUI view of the data/metadata
# ------------------------------------------------------------------------

def load_json(file_name):

    try:
        f = open(file_name)
        data = json.load(f)
    except:
        data = None
    return data