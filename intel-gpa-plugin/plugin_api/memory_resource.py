# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

import json
from collections import namedtuple
from typing import List, Dict

from plugin_api.api_call import ApiCall
from utils.deprecated import deprecated
import plugin_adapter_interface


MemoryResourceData = namedtuple('MemoryResourceData', ['data', 'row_pitch'])


class MemoryResource:
    def __init__(self, desc: Dict):
        self.__desc = desc
        self.__plugin_adapter_interface = plugin_adapter_interface.get_interface()

    def get_description(self) -> Dict:
        """Return a dictionary with a resource view description.
        
        Common values are available for both texture and buffer views:
        {
            'resource_space' : internal namespace of the resource id,
            'resource_id'    : resource id,
            'view_id'        : view id,
            'resource_type'  : 'buffer',
            'view_type'      : 'CBV', 'SRV', 'UAV', etc.,
            [optional] 'name': 'resource name provided by the graphics API'
        }

        Additional fields for the buffer view (when resource_type == 'buffer'):
        {
            'size'          : size in bytes,
            'offset'        : offset in bytes,
            'stride'        : stride in bytes
        }

        Additional fields for the texture view  (when resource_type == 'texture'):
        {
            'final_fb'      : true if the resource is a swap chain frame buffer,
            'format'        : 'texture format',
            'texture_type'  : '2D texture', '3D texture', 'cubemap', '2D texture array', 'cubemap array'
            'is_multisample': false,
            'first_mip'     : index of the most detailed mipmap level to use,
            'mip_count'     : the maximum number of mipmap levels for the view of the texture,
            'first_slice'   : the index of the first texture to use in an array of textures,
            'slice_count'   : number of textures in the array,
            'mips'          : [
                {
                    'width' : width,
                    'height' : height,
                    'depth' : depth for 3D textures
                },
                ...
            ]
        }
        """
        return self.__desc

    def get_usages(self) -> List[int]:
        """Return usages of current memory_resource.

        Return value is a list of memory_resource usages
        """
        return json.loads(self.__plugin_adapter_interface.get_memory_resources_usages(self.__desc["resource_space"],
                                                                                      self.__desc["resource_id"],
                                                                                      self.__desc["view_id"]))

    @deprecated("1.2", "this call does not work with multiple resources, use Resources.get_buffers_data() instead")
    def get_buffer_data(self, event_call: ApiCall, extract_before: bool = False, timeout_ms: int = 20000) -> MemoryResourceData:
        """Return buffer data for a given API call.

        Keyword arguments:
        event_call     -- API call
        extract_before -- True if you need data before executing a given API call. Default value is False
        timeout_ms     -- period of time in milliseconds to wait for results. Default value is 20000

        Return class with the following members:
            data      -- [list of raw bytes]
            row_pitch -- the row pitch, or width, or physical size (in bytes) of the data
        """
        request = {
            'resource_space': self.__desc["resource_space"],
            'resource_id': self.__desc["resource_id"],
            'mip': 0,
            'slice': 0,
            'call_id': event_call.get_description()["id"],
            'extract_before': extract_before
        }

        res = self.__plugin_adapter_interface.get_subresource_data(
            [request], timeout_ms)

        output_items = [item for _, item in res.items()]

        output_data = output_items[0].data
        output_data = output_data[self.__desc["offset"] : self.__desc["offset"] + self.__desc["size"]]
        output_row_pitch = output_items[0].row_pitch

        output = MemoryResourceData(data=output_data, row_pitch=output_row_pitch)
        return output

    @deprecated("1.2", "this call does not work with multiple resources, use Resources.get_images_data() instead")
    def get_image_data(self, mip: int, slice: int, event_call: ApiCall, extract_before: bool = False, timeout_ms: int = 60000) -> MemoryResourceData:
        """Return image data for a given API call.

        Keyword arguments:
        mip            -- the mip level of a texture
        slice          -- the index in an array of textures or z coordinate for 3d texture
        event_call     -- API call
        extract_before -- True if you need data before executing a given API call. Default value is False
        timeout_ms     -- the period of time in milliseconds to wait for results. Default value is 60000

        Return class with the following members:
            data      -- [list of raw bytes]
            row_pitch -- the row pitch, or width, or physical size (in bytes) of the data
        """

        if mip < self.__desc["first_mip"] or mip >= self.__desc["first_mip"] + self.__desc["mip_count"]:
            raise ValueError("Requested mip out of view")
        if slice < self.__desc["first_slice"] or slice >= self.__desc["first_slice"] + self.__desc["slice_count"]:
            raise ValueError("Requested slice out of view")

        request = {
            'resource_space': self.__desc["resource_space"],
            'resource_id': self.__desc["resource_id"],
            'mip': mip,
            'slice': slice,
            'call_id': event_call.get_description()["id"],
            'extract_before': extract_before
        }

        res = self.__plugin_adapter_interface.get_subresource_data(
            [request], timeout_ms)

        output_items = [item for _, item in res.items()]

        output_data = output_items[0].data
        output_row_pitch = output_items[0].row_pitch

        return MemoryResourceData(data=output_data, row_pitch=output_row_pitch)
