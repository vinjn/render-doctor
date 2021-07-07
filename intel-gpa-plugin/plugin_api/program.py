# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

import json
from typing import Any, Dict

from utils.internals import check_type
import plugin_adapter_interface


class Program:
    def __init__(self, desc: Dict[str, Any]):
        check_type(desc, dict)
        self.__plugin_adapter_interface = plugin_adapter_interface.get_interface()
        self.__desc = desc
        self.__il_sources = {}

    def get_description(self) -> Dict[str, Any]:
        """Return a dictionary with a program description.

        Return value is a dictionary of the following format:
        {
            "id" : program_id,
            "vertex" : { dictionary with shader code },
            "pixel" : {
                "hash": optional integer with shader hash in case if it is available
                "source" : string with hlsl shader code, empty if source code is not present or it is binary,
                "dxil" : string with binary code if it was captured
                ...
            },
            "geometry" : { dictionary with shader code },
            ...
        }
        """
        return self.__desc

    def get_il_source(self, shader_type: str, il_type: str, timeout_ms: int = 60000) -> str:
        """Return an intermediate shader source code for the given shader type.

        Keyword arguments:
        shader_type -- type of shader. Possible values: pixel, vertex, geometry, hull, domain, compute
        il_type     -- type of intermediate shader. Possible values: isa, dxil
        timeout_ms  -- period of time in milliseconds to wait for results. Default value is 60000
        """
        check_type(shader_type, str)
        check_type(il_type, str)

        if shader_type not in ["vertex", "pixel", "hull", "domain", "geometry", "compute"]:
            raise RuntimeError("Shader type is not recognized. Possible values: pixel, vertex, geometry, hull, domain, compute")

        if il_type not in ["isa", "dxil"]:
            raise RuntimeError("Shader source type is not recognized. Possible values: isa, dxil")

        str_id = str(self.__desc["id"])
        shader_source = None
        try:
            shader_source = self.__il_sources[str_id][shader_type][il_type]
        except:
            pa_source = json.loads(self.__plugin_adapter_interface.get_il_source(self.__desc["id"],
                                                                                 shader_type,
                                                                                 il_type,
                                                                                 timeout_ms))
            # this is just a workaround right now, since we return whole structure of source tree
            shader_source = pa_source[next(iter(pa_source))][shader_type][il_type]
            if str_id not in self.__il_sources:
                self.__il_sources[str_id] = {}
            if shader_type not in self.__il_sources[str_id]:
                self.__il_sources[str_id][shader_type] = {}
            if il_type not in self.__il_sources[str_id][shader_type]:
                self.__il_sources[str_id][shader_type][il_type] = ""
            self.__il_sources[str_id][shader_type][il_type] = shader_source
        return shader_source
