# Copyright (C) 2019-2020 Intel Corporation
# This software and the related documents are Intel copyrighted materials, and your use of them is governed by the express license under which they were provided to you ("License"). Unless the License provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents without Intel's prior written permission.
# This software and the related documents are provided as is, with no express or implied warranties, other than those that are expressly stated in the License.

import json
from typing import Dict, List, Union, Tuple, TypeVar

from utils.internals import check_type
from plugin_api.api_call import ApiCall
from plugin_api.group import Group
import plugin_adapter_interface


ApiRange = TypeVar('ApiRange', Tuple[ApiCall, ApiCall], ApiCall, Group)


class Metrics:
    def __init__(self):
        self.__plugin_adapter_interface = plugin_adapter_interface.get_interface()
        self.__metrics_descriptions = json.loads(self.__plugin_adapter_interface.get_metrics_descriptions())

    def get_metrics_descriptions(self) -> List[Dict[str, str]]:
        """Return a list of metric description objects.

        Return value is a dictionary of the following format:
        {
            "name"          : "metric name from Frame Analyzer",
            "symbolic_name" : "MetricSymbolicName",
            "type"          : "type of the metric, possible values are: Unknown, Percent, Time, Timestamp, Value, Count, Number",
            "uri"           : "URI of the metric",
            "group"         : "name of the group that includes this metric"
            "units"         : "units of the metric, possible values are: %, us, ns, ms, MHz, threads, messages, texels, pixels, cycles, bytes, kbytes, Mbytes, number"
        }
        """
        return self.__metrics_descriptions

    @staticmethod
    def __get_leftmost_or_rightmost_child(node: Union[list, tuple, Group, ApiCall], leftmost: bool) -> ApiCall:
        index = 0 if leftmost else -1
        if isinstance(node, list):
            return Metrics.__get_leftmost_or_rightmost_child(node[index], leftmost)
        elif isinstance(node, tuple):
            return Metrics.__get_leftmost_or_rightmost_child(node[index], leftmost)
        elif isinstance(node, Group):
            if not node.get_children():
                raise RuntimeError('Unexpected empty group')
            return Metrics.__get_leftmost_or_rightmost_child(node.get_children()[index], leftmost)
        elif isinstance(node, ApiCall):
            return node
        else:
            raise RuntimeError('Unknown entity type found: {}'.format(type(node)))

    @staticmethod
    def __get_leftmost_and_rightmost_child(node: Union[list, tuple, Group, ApiCall]) -> ApiCall:
        return Metrics.__get_leftmost_or_rightmost_child(node, True), Metrics.__get_leftmost_or_rightmost_child(node, False)

    def get_metrics_for_ranges(self,
                               ranges: List[ApiRange],
                               metric_names: List[str],
                               transpose_table: bool = False,
                               timeout_ms: int = 60000) -> Dict[Union[str, ApiRange], Union[ApiRange, str]]:
        """Request metrics for a list of ranges and a list of metric symbolic names.

        Keyword arguments:
        ranges          -- list-like of different object types. All ranges must be sorted from the the lowest to the highest range without any intersections inside.
            Possible objects are:
                * single ApiCall object
                * tuple of (ApiCall, ApiCall) objects where the first one is start-range and the second one is end-range
                * Group object
        metrics_name    -- list of metric names to measure
        transpose_table -- if True, then the return table is in transposed format. Default value is False
        timeout_ms      -- period of time in milliseconds to wait for results. Default value is 60000

        Return value is a dictionary of the following format:
        {
            "MetricName1" : {
                range1: value,
                range2: value,
                ....
                rangeM: value,
            },
            ...
            "MetricNameN" : {
                range1: value,
                range2: value,
                ....
                rangeM: value,
            }
        }

        Transposed results:
        {
           range1 :
           {
             "MetricName1" : value,
             "MetricName2" : value,
             ...
             "MetricNameN" : value,
           },
           ...
           rangeN :
           {
             "MetricName1" : value,
             "MetricName2" : value,
             ...
             "MetricNameN" : value,
           }
        }
        """
        check_type(ranges, list)
        check_type(metric_names, list)

        if not ranges:
            raise RuntimeError("No ranges provided")

        if not metric_names:
            raise RuntimeError("No metrics provided")

        api_indices = []
        last_api_index = -1
        for range in ranges:
            if isinstance(range, tuple):
                if len(range) != 2:
                    raise RuntimeError("Range size is not correct: expected two calls, provided {}".format(len(range)))
                check_type(range[0], ApiCall)
                check_type(range[1], ApiCall)
            elif isinstance(range, ApiCall):
                pass
            elif isinstance(range, Group):
                pass
            else:
                raise RuntimeError(
                    'Wrong range passed as an argument: expected either tuple of ApiCall objects, single ApiCall object or Group object, got: {}'.format(type(range)))

            start_node, end_node = Metrics.__get_leftmost_and_rightmost_child(range)
            start_api_index = start_node.get_description()['id']
            end_api_index = end_node.get_description()['id']

            if last_api_index >= start_api_index:
                raise RuntimeError("Ranges intersect or are not sorted: found a call with {} index before {}".format(
                    last_api_index, start_api_index))
            if start_api_index > end_api_index:
                raise RuntimeError("Incorrect calls order in a range")

            last_api_index = end_api_index
            api_indices.append((start_api_index, end_api_index))

        for metric_name in metric_names:
            check_type(metric_name, str)

        api_indices_json = json.dumps(api_indices)
        metric_names_json = json.dumps(metric_names)

        metric_vals = json.loads(self.__plugin_adapter_interface.get_metrics_for_ranges(
            api_indices_json, metric_names_json, timeout_ms))

        metric_table = {}
        if not transpose_table:
            for metric_num, metric_name in enumerate(metric_names):
                metric_table[metric_name] = {}
                for row_num, row_data in enumerate(metric_vals):
                    metric_table[metric_name][ranges[row_num]] = row_data[metric_num]
        else:
            for row_num, row_data in enumerate(metric_vals):
                api_range = ranges[row_num]
                metric_table[api_range] = {}
                for metric_num, metric_name in enumerate(metric_names):
                    metric_table[api_range][metric_name] = row_data[metric_num]
        return metric_table
