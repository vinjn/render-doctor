# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

from plugin_api import api_log
from plugin_api import resources
from plugin_api import metrics

API_LOG_ACCESSOR = None
RESOURCES_ACCESSOR = None
METRICS_ACCESSOR = None


def get_api_log_accessor() -> api_log.ApiLog:
    """Provide access to the API log accessor instance, which is created to work with API calls in a frame."""
    global API_LOG_ACCESSOR
    if API_LOG_ACCESSOR is None:
        API_LOG_ACCESSOR = api_log.ApiLog()
    return API_LOG_ACCESSOR


def get_resources_accessor() -> resources.Resources:
    """Provide access to the resources instance, which is created to work with resources in a frame."""
    global RESOURCES_ACCESSOR
    if RESOURCES_ACCESSOR is None:
        RESOURCES_ACCESSOR = resources.Resources()
    return RESOURCES_ACCESSOR


def get_metrics_accessor() -> metrics.Metrics:
    """Provide access to the metrics accessor instance, which is created to request metrics descriptions and values."""
    global METRICS_ACCESSOR
    if METRICS_ACCESSOR is None:
        METRICS_ACCESSOR = metrics.Metrics()
    return METRICS_ACCESSOR
