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
        self.config_struct = None 

        self.base_menue = None  # ?

        self.gui_level = 1      # The hirerarchical level of the navigation
        self.nav_bar = []       # Dynamic user menue to select a tree navigation

    # ------------------------------------------------------------------------
    # Get the IP and Port of the query node
    # ------------------------------------------------------------------------
    def get_query_node(self):
        '''
        Return the "query_node" value (IP:Port) from the JSON config struct
        '''
        if self.config_struct and "gui" in self.config_struct and "query_node" in self.config_struct["gui"]:
            query_node = self.config_struct["gui"]["query_node"]
        else:
            query_node - None
        return query_node
    # ------------------------------------------------------------------------
    # Load the JSON and set main structures
    # ------------------------------------------------------------------------
    def set_gui(self, file_name = None):

        if not file_name:
            file_name = Config.GUI_VIEW    # get from system variable
        
        self.config_struct = load_json(file_name)

 
    # ------------------------------------------------------------------------
    # Set Menu names and links based on the JSON file
    # ------------------------------------------------------------------------
    def set_menue(self, gui_level = 0):
        '''
        Set the navigation menue as f (traversal level)
        '''

        if self.config_struct and not self.base_menue:
            self.base_menue = []
            if isinstance(self.config_struct, dict):
                if "gui" in self.config_struct and "children" in self.config_struct["gui"]:     # Root of JSON
                    self.create_base_menue(self.config_struct["gui"]["children"])


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
    # Get the Navigation Bar as f(level)
    # ------------------------------------------------------------------------
    def get_nav_bar(self, gui_level):
        '''
        Get the Navigation Bar as f(level)
        '''
        if gui_level:
            self.gui_level = gui_level      # Move backwards or stay on the previous leve

        if self.config_struct:
            if isinstance(self.config_struct, dict):
                if "gui" in self.config_struct and "children" in self.config_struct["gui"]:     # Root of JSON
                    json_struct = self.config_struct["gui"]["children"]     # root of JSON to use

                    for i in range(self.gui_level):
                        if i == self.gui_level - 1:
                            # Last level - get all children
                            for counter, entry in enumerate(json_struct):
                                if "name" in entry:
                                    text_name = entry["name"]       # The name to print
                                    try:
                                        url_link = url_for(text_name.lower())   # the link to use
                                    except:
                                        continue
                                    if (i + counter) < len(self.nav_bar):
                                        self.nav_bar[i + counter] = ((text_name, url_link))
                                    else:
                                        self.nav_bar.append((text_name, url_link))
                        else:
                            # Add the parents which were selected by the user
                            pass
 

     


    # ------------------------------------------------------------------------
    # Get the AnyLog command as f (level) from the user JSON configuration struct
    # ------------------------------------------------------------------------
    def get_command(self, level):
        '''
        Get the AnyLog command as f (level) from the user JSON configuration struct
        '''

        json_struct = None
        if "gui" in self.config_struct:
            json_struct = self.config_struct["gui"]
            for i in range(level):
                if "children" in json_struct:
                    json_struct = json_struct["children"]
                else:
                    json_struct = None
                    break

        if json_struct and "query" in json_struct:
            command = json_struct["query"]
        else:
            command = None
        return command      # the AL command - if available
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
