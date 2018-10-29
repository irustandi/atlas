"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

import unittest
from foundations_rest_api.v1.models.queued_job import QueuedJob
from foundations.scheduler_legacy_backend import LegacyBackend


class TestQueuedJob(unittest.TestCase):

    class MockSchedulerBackend(LegacyBackend):

        def __init__(self, expected_status, job_information):
            self._expected_status = expected_status
            self._job_information = job_information

        def get_paginated(self, start_index, number_to_get, status):
            if self._expected_status == status:
                return self._job_information

            return []

    class MockDeployment(object):

        def __init__(self, scheduler_backend_callback):
            self._scheduler_backend_callback = scheduler_backend_callback

        def scheduler_backend(self):
            return self._scheduler_backend_callback

    def setUp(self):
        from foundations.global_state import config_manager
        from foundations.global_state import deployment_manager

        deployment_manager._scheduler = None # ugh...
        self._scheduler_backend_instance = self.MockSchedulerBackend('QUEUED', [])
        self._mock_deployment = self.MockDeployment(self._scheduler_backend)

        config_manager['deployment_implementation'] = {
            'deployment_type': self._mock_deployment,
        }

    def tearDown(self):
        from foundations.global_state import config_manager

        keys = list(config_manager.config().keys())
        for key in keys:
            del config_manager.config()[key]

    def test_has_job_id(self):
        from uuid import uuid4

        job_id = str(uuid4())
        job = QueuedJob(job_id=job_id)

        self.assertEqual(job_id, job.job_id)

    def test_has_user(self):
        job = QueuedJob(user='Louis')
        self.assertEqual('Louis', job.user)

    def test_has_user_different_user(self):
        job = QueuedJob(user='Lenny')
        self.assertEqual('Lenny', job.user)

    def test_has_submitted_time(self):
        job = QueuedJob(submitted_time=484848448448844)
        self.assertEqual(484848448448844, job.submitted_time)

    def test_has_submitted_time_different_params(self):
        job = QueuedJob(submitted_time=984222255555546)
        self.assertEqual(984222255555546, job.submitted_time)

    def test_all_is_empty_response(self):
        self.assertEqual([], QueuedJob.all().evaluate())

    def test_all_returns_job_information_from_scheduler(self):
        from foundations.scheduler_job_information import JobInformation

        job_information = JobInformation('00000000-0000-0000-0000-000000000000', 123456789, 9999, 'QUEUED', 'soju hero')
        self._scheduler_backend_instance = self.MockSchedulerBackend('QUEUED', [job_information])

        expected_job = QueuedJob(job_id='00000000-0000-0000-0000-000000000000', user='soju hero', submitted_time='1973-11-29T21:33:09')
        result = QueuedJob.all().evaluate()[0]

        self.assertEqual(expected_job, result)

    def test_all_returns_job_information_from_scheduler_with_different_jobs(self):
        from foundations.scheduler_job_information import JobInformation

        job_information = JobInformation('00000000-0000-0000-0000-000000000000', 987654321, 4444, 'QUEUED', 'soju zero')
        job_information_two = JobInformation('00000000-0000-0000-0000-000000000001', 888888888, 3214, 'QUEUED', 'potato hero')
        self._scheduler_backend_instance = self.MockSchedulerBackend('QUEUED', [job_information, job_information_two])

        expected_job = QueuedJob(job_id='00000000-0000-0000-0000-000000000000', user='soju zero', submitted_time='2001-04-19T04:25:21')
        expected_job_two = QueuedJob(job_id='00000000-0000-0000-0000-000000000001', user='potato hero', submitted_time='1998-03-03T01:34:48')
        expected_jobs = [expected_job, expected_job_two]
        result = QueuedJob.all().evaluate()

        self.assertEqual(expected_jobs, result)

    def _scheduler_backend(self):
        return self._scheduler_backend_instance