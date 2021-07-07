# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from typing import List


class Group:
    def __init__(self, name: str, children: List):
        self.name = name
        self.children = children

    def get_children(self) -> List:
        return self.children

    def get_name(self) -> str:
        return self.name
