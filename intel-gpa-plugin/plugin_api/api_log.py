# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from collections import defaultdict
from enum import Enum
import json
from typing import List, Dict, Any, Union

import plugin_adapter_interface

from plugin_api import api_call, group

from utils import common
from utils.deprecated import deprecated


class GroupingType(Enum):
    RENDER_TARGET = 'Render Target'
    COMMAND_LIST = 'Command List'
    SHADER_SET = 'Shader Set'
    PIPELINE_STATE = 'Pipeline State'
    DEBUG_REGION = 'Debug Region'


class ApiLog:
    def __init__(self):
        self.__full_by_group = defaultdict(lambda: [])
        self.__plugin_adapter_interface = plugin_adapter_interface.get_interface()
        all_calls = common.all_calls_from_node(self.get_calls())
        self.__events = [x for x in all_calls if x.get_description()['is_event']]

    @staticmethod
    def __parse_groups(json_group: Dict[str, Any]) -> group.Group:
        children = []
        for el in json_group['children']:
            if el['type'] == 'apicall':
                children.append(api_call.ApiCall(el))
            elif el['type'] == 'group':
                children.append(ApiLog.__parse_groups(el))
        return group.Group(json_group['name'], children)

    @deprecated(version='1.1', reason='get_full does not support grouping, use get_calls instead')
    def get_full(self) -> List:
        """Return a full list of api_call objects."""
        return list(common.all_calls_from_node(self.get_calls()))

    @deprecated(version='1.1', reason='get_events does not support grouping, use get_calls instead')
    def get_events(self) -> List:
        """Return a planar list of api_call objects that are events."""
        return self.__events

    def __get_frames(self) -> List[Union[api_call.ApiCall, group.Group]]:
        # workaround
        # this is a temporary method to access frames until we have special accessor
        output = []
        apilog = json.loads(self.__plugin_adapter_interface.get_apilog("Frame"))
        for el in apilog:
            if el['type'] == 'apicall':
                output.append(api_call.ApiCall(el))
            elif el['type'] == 'group':
                output.append(ApiLog.__parse_groups(el))
        return output

    def get_calls(self, grouping_type: GroupingType = None) -> List[Union[api_call.ApiCall, group.Group]]:
        if grouping_type is not None and not isinstance(grouping_type, GroupingType):
            raise RuntimeError('grouping_type arg must be one of GroupingType enumeration')

        if grouping_type not in self.__full_by_group:
            apilog = json.loads(self.__plugin_adapter_interface.get_apilog(grouping_type.value if grouping_type is not None else 'Event'))
            for el in apilog:
                if el['type'] == 'apicall':
                    self.__full_by_group[grouping_type].append(api_call.ApiCall(el))
                elif el['type'] == 'group':
                    self.__full_by_group[grouping_type].append(ApiLog.__parse_groups(el))
        return self.__full_by_group[grouping_type]
