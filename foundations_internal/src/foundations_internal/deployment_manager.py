"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""


class DeploymentManager(object):

    def __init__(self, config_manager):
        self._config_manager = config_manager

    def simple_deploy(self, stage, job_name, job_params):
        import uuid

        from foundations.job import Job

        if not job_name:
            job_name = str(uuid.uuid4())
        job = Job(stage, **job_params)

        deployment = self.deploy({}, job_name, job)
        self._record_project(stage)
        return deployment

    def deploy(self, deployment_config, job_name, job):
        from foundations import log_manager
        from foundations_contrib.local_shell_job_deployment import LocalShellJobDeployment
        from foundations.global_state import message_router, current_foundations_context
        from foundations_internal.deployment.job_preparation import prepare_job

        logger = log_manager.get_logger(__name__)

        deployment = self._create_deployment(job_name, job)
        deployment.config().update(deployment_config)
        project_name = current_foundations_context().project_name()

        # TODO: Make this not stupid
        if isinstance(deployment, LocalShellJobDeployment):
            deployment.deploy()
            logger.info("Job submitted with ID '{}' in project '{}'.".format(job_name, project_name))
        else:
            deployment.deploy()
            logger.info("Job submitted with ID '{}' in project '{}'.".format(job_name, project_name))

        return deployment

    def _record_project(self, stage):
        constructor, constructor_args, constructor_kwargs = self.project_listing_constructor_and_args_and_kwargs()
        listing = constructor(*constructor_args, **constructor_kwargs)
        listing.track_pipeline(
            stage.pipeline_context().provenance.project_name)

    def _create_deployment(self, job_name, job):
        from foundations_contrib.job_source_bundle import JobSourceBundle

        deployment_constructor, constructor_args, constructor_kwargs = self._deployment_constructor_and_args_and_kwargs()

        job_source_bundle = JobSourceBundle.for_deployment()

        return deployment_constructor(job_name, job, job_source_bundle, *constructor_args, **constructor_kwargs)

    def _deployment_constructor_and_args_and_kwargs(self):
        return self._config_manager.reflect_constructor('deployment', 'deployment', DeploymentManager._create_default_deployment)

    def project_listing_constructor_and_args_and_kwargs(self):
        return self._config_manager.reflect_constructor('project_listing', 'project_listing', DeploymentManager._create_default_project_listing)

    @staticmethod
    def _create_default_project_listing():
        from foundations_contrib.null_pipeline_archive_listing import NullPipelineArchiveListing
        return NullPipelineArchiveListing()

    @staticmethod
    def _create_default_deployment(job_name, job, job_source_bundle):
        from foundations_contrib.local_shell_job_deployment import LocalShellJobDeployment
        return LocalShellJobDeployment(job_name, job, job_source_bundle)
