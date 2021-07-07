# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from typing import Any, Dict

from utils.internals import check_type


class States:
    def __init__(self, desc: Dict[str, Any]):
        check_type(desc, dict)
        self.__desc = desc

    def get_description(self) -> Dict[str, Any]:
        """Return a dictionary with states description.

        Return value is a dictionary of the following format:
        {
            "name_of_state" : {state_fields_description},
            "Blending" : {
                "state_field_name" : "state_field_value",
                "Alpha to coverage" : 0,
                "Independent blend enable" : 0,
                "Factors" : [0, 0, 0, 0],
                "Logic Op" : "COPY_INVERTED",
                "Front Face Stencil-Depth Fail Op" : "Undefined",
                "RT Write Mask" : 0xff,
                "Logic Op Enable" : false,
                ...
            },
            ...
        }
        """
        return self.__desc
