# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

import json
from typing import List, Dict, Optional

from plugin_api.api_call import ApiCall
from plugin_api.memory_resource import MemoryResource, MemoryResourceData
from plugin_api.program import Program
import plugin_adapter_interface


class BufferRequest:
    def __init__(self, buffer: MemoryResource, call: ApiCall, extract_before: bool = False):
        self.buffer = buffer
        self.call = call
        self.extract_before = extract_before


class ImageRequest:
    def __init__(self, image: MemoryResource, mip: int, slice_: int, call: ApiCall, extract_before: bool = False):
        self.image = image
        self.mip = mip
        self.slice_ = slice_
        self.call = call
        self.extract_before = extract_before


class Resources:
    def __init__(self):
        self.__plugin_adapter_interface = plugin_adapter_interface.get_interface()
        self.__memory_resources = {}

        tmp = json.loads(self.__plugin_adapter_interface.get_memory_resources())
        for res_id, view_list in tmp.items():
            self.__memory_resources[res_id] = [MemoryResource(x) for x in view_list]

        tmp = json.loads(self.__plugin_adapter_interface.get_programs())
        self.__programs = [Program(x) for x in tmp]

    def get_memory_resources(self) -> Dict[str, List[MemoryResource]]:
        """
        Return a dictionary of memory resources and views.
        {
           "resource_id_1": [list of MemoryResource objects],
           "resource_id_2": [list of MemoryResource objects]
        }
        """
        return self.__memory_resources

    def get_programs(self) -> List[Program]:
        """Return list of program objects."""
        return self.__programs

    def get_buffers_data(self, requests: List[BufferRequest], timeout: int = 20000) -> Dict[BufferRequest, MemoryResourceData]:
        '''Return data of the buffers.
        Make sure that you do not request the same buffer on the call twice.

        Keyword arguments:
        requests -- list of BufferRequest objects with the buffers content needed to be obtained
        timeout -- timeout for execution in milliseconds
        '''
        pi_requests = []
        resource_ids_per_call = set()
        for request in requests:
            buffer_desc = request.buffer.get_description()
            resource_id = buffer_desc['resource_id']
            call_id = request.call.get_description()['id']
            if (resource_id, call_id) in resource_ids_per_call:
                raise RuntimeError('Resource request with {} id on call {} is duplicated'.format(resource_id, call_id))
            resource_ids_per_call.add(tuple([resource_id, call_id]))

            pi_requests.append({
                'resource_space': buffer_desc['resource_space'],
                'resource_id': resource_id,
                'mip': 0,
                'slice': 0,
                'call_id': call_id,
                'extract_before': request.extract_before
            })

        result = self.__plugin_adapter_interface.get_subresource_data(pi_requests, timeout)

        def find_buffer(requests: List[BufferRequest], res_id: int, call_id: int, extract_before: bool) -> Optional[BufferRequest]:
            for request in requests:
                if all([request.buffer.get_description()['resource_id'] == res_id,
                        request.call.get_description()['id'] == call_id,
                        request.extract_before == extract_before
                        ]):
                    return request
            return None

        output = {}
        for key, value in result.items():
            _, res_id, _, _, call_id, extract_before = key

            buffer_request = find_buffer(requests, res_id, call_id, extract_before)
            if not buffer_request:
                raise RuntimeError('Request failed')
            buffer_offset = buffer_request.buffer.get_description()['offset']
            buffer_size = buffer_request.buffer.get_description()['size']

            data = value.data[buffer_offset: buffer_offset + buffer_size]
            output[buffer_request] = MemoryResourceData(data=data, row_pitch=value.row_pitch)
        return output

    def get_images_data(self, requests: List[ImageRequest], timeout: int = 60000) -> Dict[ImageRequest, MemoryResourceData]:
        '''Return data of the images.
        Make sure that you do not request the same image on the call twice.

        Keyword arguments:
        requests -- list of ImageRequest objects with the images content needed to be obtained
        timeout -- timeout for execution in milliseconds
        '''
        pi_requests = []
        resource_ids_per_call = set()
        for request in requests:
            image_desc = request.image.get_description()
            resource_id = image_desc['resource_id']
            call_id = request.call.get_description()['id']
            if (resource_id, call_id) in resource_ids_per_call:
                raise RuntimeError('Resource request with {} id on call {} is duplicated'.format(resource_id, call_id))
            resource_ids_per_call.add(tuple([resource_id, call_id]))

            pi_requests.append({
                'resource_space': image_desc["resource_space"],
                'resource_id': resource_id,
                'mip': request.mip,
                'slice': request.slice_,
                'call_id': call_id,
                'extract_before': request.extract_before
            })

        result = self.__plugin_adapter_interface.get_subresource_data(pi_requests, timeout)

        def find_image(requests: List[ImageRequest], res_id: int, mip: int, slice_: int, call_id: int, extract_before: bool) -> Optional[ImageRequest]:
            for request in requests:
                if all([request.image.get_description()['resource_id'] == res_id,
                        request.mip == mip,
                        request.slice_ == slice_,
                        request.call.get_description()['id'] == call_id,
                        request.extract_before == extract_before]):
                    return request
            return None

        output = {}
        for key, value in result.items():
            _, res_id, mip, slice_, call_id, extract_before = key
            image_request = find_image(requests, res_id, mip, slice_, call_id, extract_before)
            if not image_request:
                raise RuntimeError('Request failed')
            output[image_request] = MemoryResourceData(data=value.data, row_pitch=value.row_pitch)
        return output
