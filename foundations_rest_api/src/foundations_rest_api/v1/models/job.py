"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Dariem Perez <d.perez@dessa.com>, 11 2018
"""

from foundations_rest_api.v1.models.property_model import PropertyModel


class Job(PropertyModel):

    job_id = PropertyModel.define_property()
    user = PropertyModel.define_property()
    job_parameters = PropertyModel.define_property()
    input_params = PropertyModel.define_property()
    output_metrics = PropertyModel.define_property()
    status = PropertyModel.define_property()
    start_time = PropertyModel.define_property()
    completed_time = PropertyModel.define_property()

    @staticmethod
    def all(project_name=None):
        from foundations_core_rest_api_components.lazy_result import LazyResult

        def _all():
            return Job._all_internal(project_name)

        return LazyResult(_all)

    @staticmethod
    def _all_internal(project_name):
        return list(Job._load_jobs(project_name))

    @staticmethod
    def _load_jobs(project_name):
        running_jobs = Job._get_running_jobs(project_name)
        completed_jobs = Job._get_completed_jobs(project_name)
        all_jobs = running_jobs + completed_jobs
        Job._default_order(all_jobs)
        return all_jobs

    @staticmethod
    def _default_order(jobs):

        def get_sort_key(job):
            return job.start_time

        jobs.sort(key=get_sort_key, reverse=True)

    @staticmethod
    def _get_running_jobs(project_name):
        from foundations_contrib.global_state import deployment_manager

        jobs = []
        for info in deployment_manager.scheduler().get_job_information('RUNNING'):
            job = Job(
                job_id=info.uuid(),
                user=info.user_submitted(),
                start_time=info.submission_datetime().isoformat(),
                completed_time=None,
                status='Running',
                job_parameters={},
                input_params=[],
                output_metrics={}
            )
            jobs.append(job)
        return jobs

    @staticmethod
    def _get_completed_jobs(project_name):
        from foundations_contrib.models.pipeline_context_listing import PipelineContextListing
        from foundations_rest_api.v1.models.completed_job import CompletedJob

        jobs = []

        def _loop_body(job_id, context):
            job_properties = CompletedJob._job_properties(context, job_id)
            if project_name is None or project_name == job_properties['project_name']:
                del job_properties['project_name']
                jobs.append(Job(**job_properties))

        for job_id, context in list(PipelineContextListing.pipeline_contexts()):
            _loop_body(job_id, context)

        return jobs
