"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

from foundations_rest_api.v1.models.property_model import PropertyModel


class RunningJob(PropertyModel):

    job_id = PropertyModel.define_property()
    user = PropertyModel.define_property()
    job_parameters = PropertyModel.define_property()
    input_params = PropertyModel.define_property()
    output_metrics = PropertyModel.define_property()
    start_time = PropertyModel.define_property()

    @staticmethod
    def all():
        """Placeholder method that will eventually return all RunningJobs

        Returns:
            list<RunningJob> -- All queued jobs
        """
        from foundations_core_rest_api_components.lazy_result import LazyResult

        def _all():
            from foundations_contrib.global_state import deployment_manager

            jobs = []
            for info in deployment_manager.scheduler().get_job_information('RUNNING'):
                job = RunningJob(
                    job_id=info.uuid(),
                    user=info.user_submitted(),
                    start_time=info.submission_datetime().isoformat(),
                    job_parameters={},
                    input_params=[],
                    output_metrics={}
                )
                jobs.append(job)

            return jobs

        return LazyResult(_all)

    @staticmethod
    def contexts():
        raise NotImplementedError()

    @staticmethod
    def load_context(archiver):
        from foundations_internal.pipeline_context import PipelineContext

        context = PipelineContext()
        context.load_stage_log_from_archive(archiver)
        context.load_provenance_from_archive(archiver)

        return context
