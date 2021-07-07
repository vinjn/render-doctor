# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from typing import Any, Dict, List, NoReturn

from utils import common


def check_type(val: Any, val_type: Any) -> NoReturn:
    if not isinstance(val, val_type):
        raise TypeError(
            "Incorrect type {}. Should be {}".format(type(val), val_type))


def dictionary_has_key_value(target: Dict, values: Dict) -> bool:
    for key, value in values.items():
        if key not in target.keys():
            return False
        if target[key] != value:
            return False
    return True


def search_key_values_in_dict(target: Dict, values: Dict) -> bool:
    if dictionary_has_key_value(target, values):
        return True
    for k in target.keys():
        if common.check_object_by_request(target[k], values):
            return True
    return False


def search_key_value_in_list(target: List, values: Dict) -> bool:
    for element in target:
        if common.check_object_by_request(element, values):
            return True
    return False
