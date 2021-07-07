# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from logs import messages

def deprecated(version, reason=None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if reason is not None:
                messages.debug('Function {} is deprecated since version {}. Reason: {}.'.format(function.__name__, version, reason))
            else:
                messages.debug('Function {} is deprecated since version {}.'.format(function.__name__, version))
            return function(*args, **kwargs)
        return wrapper
    return decorator
