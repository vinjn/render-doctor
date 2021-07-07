# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from enum import Enum
from typing import Any, Dict, List, Generator, Union

from utils.deprecated import deprecated
from utils.internals import check_type, search_key_values_in_dict, search_key_value_in_list

from plugin_api.group import Group
from plugin_api.api_call import ApiCall
from plugin_api.memory_resource import MemoryResource


def check_object_by_request(target: Union[Dict, List], request: Dict) -> bool:
    """Return True if a target has an entry that matches a given request.

    Keyword arguments:
    target -- a dictionary or a list to search in
    request -- a dictionary object. Keys represent names of fields to look in, values represent what to look for
    """
    check_type(request, dict)

    if isinstance(target, dict):
        return search_key_values_in_dict(target, request)
    elif isinstance(target, list):
        return search_key_value_in_list(target, request)


class MessageSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ResultArea(Enum):
    APILOG = "apilog"
    RESOURCES = "resources"


def __construct_result(area: ResultArea, id: int, object_type: str,
                       severity: Union[str, MessageSeverity],
                       description: str = None, usages: List = None) -> Dict[str, Any]:
    """Return entity that describes a rule's result.

    area        -- string that keeps area of result. Possible values are: apilog, resources
    id          -- identifier of api call or resource
    object_type -- type of the return value to determine which object is returned if IDs are the same
    severity    -- string with severity of the result. Possible values are: warning, error, info
    description -- optional string with an additional result description
    usages      -- optional list of calls where resources is used if resource passed in 'area' parameter
    """
    check_type(area, ResultArea)
    check_type(id, int)
    check_type(object_type, str)
    check_type(severity, (str, MessageSeverity))

    output = {
        "area": area.value,
        "id": id,
        "type": object_type,
        "severity": severity.value if isinstance(severity, MessageSeverity) else severity
    }

    if description is not None:
        output["description"] = str(description)

    if usages is not None:
        output["usages"] = usages

    return output


@deprecated(version='1.1', reason='call_to_result does not work with results from api_log.get_calls_by_grouping, use node_to_result instead and += operator with the result of your plugin')
def call_to_result(call: ApiCall, severity: Union[str, MessageSeverity], description: str = None) -> Dict:
    """Return the entity that describes a plugin result for a given call object.

    Keyword arguments:
    call -- resulting API call
    severity -- error significance. Possible values: 'info', 'warning', 'error' or members of MessageSeverity enumeration
    description -- optional description for a user
    """
    result = node_to_result(call, severity, description)
    if len(result) != 1:
        raise RuntimeError("Must contain only one call")
    return result[0]


def node_to_result(node: Union[ApiCall, Group], severity: MessageSeverity, description: str = None) -> List[Dict]:
    """Return the entity that describes a plugin result for a given call or group object.

    Keyword arguments:
    node -- resulting API node. May be either group or API call
    severity -- error significance. Possible values: members of MessageSeverity enumeration
    description -- optional description for a user
    """
    output = []
    for child in all_calls_from_node(node):
        output.append(__construct_result(ResultArea.APILOG,
                                         child.get_description()["id"],
                                         child.__class__.__name__, severity,
                                         description))
    return output


def resource_to_result(resource: MemoryResource, severity: MessageSeverity, description: str = None) -> Dict:
    """Return the entity that describes a plugin result for a given resource object. Possible objects: memory object and program.

    Keyword arguments:
    resource -- resulting resource
    severity -- error significance. Possible values: MessageSeverity enumeration
    description -- optional description for a user
    """
    return __construct_result(ResultArea.RESOURCES,
                              resource.get_description()["resource_id"],
                              resource.__class__.__name__, severity,
                              description, resource.get_usages())


def all_calls_from_node(node: Union[List, Group, ApiCall]) -> Generator:
    """Return the list of calls from the group or list of calls. All groups are recursively expanded producing flat list of ApiCall objects.

    Keyword arguments:
    node -- group or list to make flat
    """

    if isinstance(node, list):
        for element in node:
            for smth in all_calls_from_node(element):
                yield smth
    elif isinstance(node, Group):
        if not node.get_children():
            return
        for inner_child in node.get_children():
            for smth in all_calls_from_node(inner_child):
                yield smth
    elif isinstance(node, ApiCall):
        yield node
