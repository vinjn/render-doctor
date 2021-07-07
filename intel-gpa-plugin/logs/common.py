# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

import os
import inspect
from typing import Union, Tuple

def __find_parent() -> Union[Tuple[str, str], Tuple[None, None]]:
    current_frame = inspect.currentframe()
    while current_frame is not None:
        prev_frame = current_frame.f_back
        filename, _, _, _, _ = inspect.getframeinfo(current_frame)

        if prev_frame is None or os.path.basename(filename) == '__init__.py':
            module_path = os.path.split(os.path.abspath(filename))[0]
            plugin_name = os.path.split(module_path)[-1]
            return module_path, plugin_name
        current_frame = prev_frame

    return None, None
