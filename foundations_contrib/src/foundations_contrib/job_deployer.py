"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

def deploy_job(pipeline_context_wrapper, job_name, job_params):
    from foundations_contrib.global_state import deployment_manager, log_manager
    from foundations_contrib.deployment_wrapper import DeploymentWrapper

    logger = log_manager.get_logger(__name__)
    logger.info("Job submission started. Ctrl-C to cancel.")

    job_deployment = deployment_manager.simple_deploy(pipeline_context_wrapper, job_name, job_params)
    return DeploymentWrapper(job_deployment)