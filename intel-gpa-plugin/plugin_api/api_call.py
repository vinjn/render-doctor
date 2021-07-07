# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

import json
from typing import Dict, Any

import plugin_adapter_interface

class ApiCall:
    def __init__(self, desc: Dict):
        self.__internal_desc = self.__fill_internal_desc(desc)
        self.__delete_from_desc(desc)
        self.__desc = desc
        self.__plugin_adapter_interface = plugin_adapter_interface.get_interface()
        self.__bindings = {}

    def __fill_internal_desc(self, desc):
        internal_keys = ['group']
        internal_desc = {}

        for key in internal_keys:
            if key in desc.keys() and key not in internal_desc.keys():
                internal_desc[key] = desc[key]

        if internal_desc:
            return internal_desc
        else:
            return None

    def __delete_from_desc(self, desc):
        keys_to_delete = ['group', 'type']
        for key in keys_to_delete:
            if key in desc.keys():
                del desc[key]

    def __get_internal_desc(self):
        return self.__internal_desc

    def get_description(self) -> Dict[str, Any]:
        """Return a dictionary with information about the API call.

        Return value is a dictionary of the following format:
        {
            'id' : call_id,
            'name' : 'OMSetRenderTargets',
            'is_event': false,
            'arguments' : [
                {
                    'name' : 'NumRenderTargetDescriptors',
                    'type' : 'UINT',
                    'value' : 3
                },
                {
                    'name' : 'pRenderTargetDescriptors',
                    'type' : 'const D3D12_CPU_DESCRIPTOR_HANDLE*',
                    'value' : [
                        'name' : '*pRenderTargetDescriptors',
                        'type' : 'D3D12_CPU_DESCRIPTOR_HANDLE',
                        'value':  [
                            {
                                'name' : 'DescriptorHeap',
                                'type' : 'ID3D12DescriptorHeap*',
                                'value' : 12
                            },
                            {
                                'name' : 'Offset',
                                'type' : 'UINT64',
                                'value'' : 64
                            },
                            {
                                'name' : 'pResource',
                                'type' : 'ID3D12Resource*',
                                'value' : 16
                            }
                        ]
                    ]
                }
            ]
        }
        """
        return self.__desc

    def get_bindings(self) -> Dict[str, Any]:
        """Return the information about bindings of the API call.

        Return value is a dictionary of the following format:
        {
            "inputs" : [list of bound MemoryResource objects],
            "execution" : {
                "program" : optional program object
                "states"  : optional states object
            },
            "outputs" : [list of bound MemoryResource objects],
            "metadata" :
            {
                "input_geometry" : {
                    "index_buffer" : resource_id,
                    "vertex_buffers" : [
                        {
                            "buffer" : resource_id,
                            "layout" : {
                                "name": "POSITION", "format": "R32G32B32_FLOAT", "offset": "0"
                            }
                        }
                    ]
                }
            }
        }
        """
        from plugin_api import memory_resource, program, states

        if not self.__desc["is_event"]:
            raise RuntimeError("The call is not event")

        event_id_str = str(self.__desc["id"])
        if event_id_str not in self.__bindings:
            tmp = json.loads(self.__plugin_adapter_interface.get_event_bindings(self.__desc["id"]))
            self.__bindings[event_id_str] = {"execution":{}, "metadata":{}}
            if "inputs" in tmp:
                self.__bindings[event_id_str]["inputs"] = [memory_resource.MemoryResource(x) for x in tmp["inputs"]]
            if "outputs" in tmp:
                self.__bindings[event_id_str]["outputs"] = [memory_resource.MemoryResource(x) for x in tmp["outputs"]]
            if "execution" in tmp:
                if "program" in tmp["execution"]:
                    self.__bindings[event_id_str]["execution"]["program"] = program.Program(tmp["execution"]["program"])
                if "states" in tmp["execution"]:
                    self.__bindings[event_id_str]["execution"]["states"] = states.States(tmp["execution"]["states"])
            if "metadata" in tmp:
                self.__bindings[event_id_str]["metadata"] = tmp["metadata"]
        return self.__bindings[event_id_str]
