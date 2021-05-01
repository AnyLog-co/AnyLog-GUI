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

import json
import sys
from json.decoder import JSONDecodeError

# -----------------------------------------------------------------------------------
# Objects to describe a tree hierarchy used in output_tree.html
# -----------------------------------------------------------------------------------
class TreeNode():

    def __init__(self, **params):

        self.name = None  # The root node
        self.is_anchor = False      # The root node
        self.id = None              # The ID of the entry
        self.first_child = True        # The entry is at the top of the list
        self.last_child = None        # The entry is at the end of the list
        self.key = None             # Key to display
        self.value = None           # The value to display
        self.children = []

        # Setup params
        for key, value in params.items():
            setattr(self, key, value)

    # -----------------------------------------------------------------------------------
    # Add a child to the list of nodes
    # -----------------------------------------------------------------------------------
    def add_child(self, **params):
        '''
        Add a new child to thee current node, return the child
        '''

        if not len(self.children):
            params['first_child'] = True       # First child
        params['last_child'] = True


        child_node = TreeNode( **params )
        self.children.append( child_node )

        return child_node








