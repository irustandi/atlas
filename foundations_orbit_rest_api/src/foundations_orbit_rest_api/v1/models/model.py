"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

from foundations_core_rest_api_components.common.models.property_model import PropertyModel

class Model(PropertyModel):

    model_name = PropertyModel.define_property()
    default = PropertyModel.define_property()
    status = PropertyModel.define_property()
    created_by = PropertyModel.define_property()
    created_at = PropertyModel.define_property()
    description = PropertyModel.define_property()
    entrypoints = PropertyModel.define_property()
    validation_metrics = PropertyModel.define_property()

    @staticmethod
    def all(**kwargs):
        from foundations_core_rest_api_components.lazy_result import LazyResult

        def _all():
            return []

        return LazyResult(_all)