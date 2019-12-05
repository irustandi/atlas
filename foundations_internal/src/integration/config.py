"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Katherine Bancroft <k.bancroft@dessa.com>, 06 2018
"""

def _configure():
    from foundations_contrib.global_state import current_foundations_context
    current_foundations_context().pipeline_context().file_name = 'integration-test-job'

_configure()