"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""


class DataContractOptions(object):
    
    def __init__(self, check_row_count=None, check_special_values=None, check_distribution=None, check_min_max=None):
        self.check_row_count = check_row_count
        self.check_special_values = check_special_values
        self.check_distribution = check_distribution
        self.check_min_max = check_min_max

    def __eq__(self, other):
        return isinstance(other, DataContractOptions) \
            and self._other_attributes_equal(other)

    def _other_attributes_equal(self, other):
        return self.check_row_count == other.check_row_count \
            and self.check_special_values == other.check_special_values \
            and self.check_distribution == other.check_distribution \
            and self.check_min_max == other.check_min_max


def _equality_check(value, other_value):
    import math

    if math.isnan(value):
        return math.isnan(other_value)

    return value == other_value

def _zipped_elements_equal(values, other_values):
    for value, other_value in zip(values, other_values):
        if not _equality_check(value, other_value):
            return False

    return True