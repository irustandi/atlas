"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

import unittest
from mock import Mock


class TestJobDataProducers(unittest.TestCase):

    def setUp(self):
        from acceptance.cleanup import cleanup
        from foundations.global_state import redis_connection

        cleanup()
        self._redis = redis_connection

    def test_produces_proper_data(self):
        from foundations import create_stage
        from foundations import Hyperparameter
        from foundations import log_metric
        from foundations_contrib.job_data_redis import JobDataRedis

        @create_stage
        def dummy_data():
            return 999

        @create_stage
        def function(some_argument, some_placeholder, some_stage):
            log_metric('hello', 1)
            log_metric('hello', 2)
            log_metric('world', 3)
            return 5

        stage_parameter = dummy_data()
        stage = function(
            999,
            some_placeholder=Hyperparameter('some_run_data'),
            some_stage=stage_parameter
        )
        deployment = stage.run(some_run_data=777, job_name='successful_job')
        deployment.wait_for_deployment_to_complete()

        all_job_data = JobDataRedis.get_all_jobs_data('default', self._redis, True)

        job_data = all_job_data[0]
        self.assertEqual('default', job_data['project_name'])
        self.assertEqual('successful_job', job_data['job_id'])
        self.assertEqual('default', job_data['user'])
        self.assertEqual('completed', job_data['status'])
        self.assertTrue(isinstance(job_data['start_time'], float))
        self.assertTrue(isinstance(job_data['completed_time'], float))
        self.assertTrue(len(job_data['job_parameters']))
        self.assertTrue(len(job_data['input_params']))
        self.assertTrue(len(job_data['output_metrics']))

    def test_produces_completed_job_data(self):
        from foundations import create_stage
        from foundations import Hyperparameter
        from foundations import log_metric
        from foundations.global_state import foundations_context
        from foundations_internal.fast_serializer import deserialize
        from time import time

        @create_stage
        def dummy_data():
            return 999

        @create_stage
        def function(some_argument, some_placeholder, some_stage):
            log_metric('hello', 1)
            log_metric('hello', 2)
            log_metric('world', 3)
            return 5

        provenance = foundations_context.pipeline_context().provenance
        provenance.project_name = 'project_with_successful_jobs'
        provenance.user_name = 'a_very_successful_user'

        stage_parameter = dummy_data()
        stage = function(
            999,
            some_placeholder=Hyperparameter('some_run_data'),
            some_stage=stage_parameter
        )
        deployment = stage.run(some_run_data=777, job_name='successful_job')
        deployment.wait_for_deployment_to_complete()
        current_time = time()

        serialized_metrics = self._redis.lrange(
            'jobs:successful_job:metrics', 0, -1)
        metrics = [deserialize(data) for data in serialized_metrics]
        metric_1, metric_2, metric_3 = metrics

        self.assertTrue(current_time - metric_1[0] < 2)
        self.assertTrue(current_time - metric_2[0] < 2)
        self.assertTrue(current_time - metric_3[0] < 2)

        self.assertEqual('hello', metric_1[1])
        self.assertEqual('hello', metric_2[1])
        self.assertEqual('world', metric_3[1])

        self.assertEqual(1, metric_1[2])
        self.assertEqual(2, metric_2[2])
        self.assertEqual(3, metric_3[2])

        metric_keys = self._redis.smembers(
            'project:project_with_successful_jobs:metrics')
        metric_keys = set([data.decode() for data in metric_keys])
        self.assertEqual(set(['hello', 'world']), metric_keys)

        state = self._redis.get('jobs:successful_job:state').decode()
        self.assertEqual('completed', state)

        project_name = self._redis.get('jobs:successful_job:project').decode()
        self.assertEqual('project_with_successful_jobs', project_name)

        input_parameter_names = self._redis.smembers(
            'projects:project_with_successful_jobs:input_parameter_names')
        input_parameter_names = set([data.decode()
                                     for data in input_parameter_names])
        self.assertEqual(
            set(['some_argument', 'some_placeholder', 'some_stage']), input_parameter_names)

        stage_times = self._redis.zrange(
            'projects:project_with_successful_jobs:stage_time', 0 , -1)

        expected_list = [b'94fc8f23ef6dced1090999229ff6f378260a640d',
                         b'efae5c309a72efdc06171132798547e1142bcb84']

        self.assertCountEqual(stage_times, expected_list)

        user_name = self._redis.get('jobs:successful_job:user').decode()
        self.assertEqual('a_very_successful_user', user_name)

        completed_time = self._redis.get(
            'jobs:successful_job:completed_time').decode()
        completed_time = float(completed_time)
        self.assertTrue(current_time - completed_time < 2)

        start_time = self._redis.get('jobs:successful_job:start_time').decode()
        start_time = float(start_time)
        self.assertTrue(current_time - start_time > 0.01)
        self.assertTrue(current_time - start_time < 10)

        creation_time = self._redis.get(
            'jobs:successful_job:creation_time').decode()
        creation_time = float(creation_time)
        self.assertTrue(current_time - creation_time > 0.01)
        self.assertTrue(current_time - creation_time < 35)

        running_jobs = self._redis.smembers(
            'project:project_with_successful_jobs:jobs:running')
        running_jobs = set([data.decode() for data in running_jobs])
        self.assertEqual(set(['successful_job']), running_jobs)

        serialized_run_parameters = self._redis.get(
            'jobs:successful_job:parameters')
        run_parameters = self._foundations_deserialize(serialized_run_parameters)
        self.assertEqual({'some_run_data': 777}, run_parameters)

        serialized_input_parameters = self._redis.get(
            'jobs:successful_job:input_parameters')
        input_parameters = self._foundations_deserialize(serialized_input_parameters)
        
        expected_input_parameters = [
            {
                'argument': {
                    'name': 'some_argument', 'value': {
                        'type': 'constant', 'value': 999
                    }
                },
                'stage_uuid': stage.uuid()
            },
            {
                'argument': {
                    'name': 'some_placeholder',
                    'value': {
                        'type': 'dynamic',
                        'name': 'some_run_data'
                    }
                },
                'stage_uuid': stage.uuid()
            },
            {
                'argument': {
                    'name': 'some_stage',
                    'value': {
                        'type': 'stage',
                        'stage_name': 'dummy_data',
                        'stage_uuid': stage_parameter.uuid()
                    }
                },
                'stage_uuid': stage.uuid()
            }
        ]
        self.assertEqual(expected_input_parameters, input_parameters)

    def test_produces_failed_job_data(self):
        from foundations import create_stage
        from foundations.utils import using_python_2

        @create_stage
        def function():
            raise Exception('I died!')

        stage = function()
        deployment = stage.run(job_name='failed_job')
        deployment.wait_for_deployment_to_complete()

        state = self._redis.get('jobs:failed_job:state').decode()
        self.assertEqual('failed', state)

        serialized_error_information = self._redis.get(
            'jobs:failed_job:error_information')
        error_information = self._foundations_deserialize(serialized_error_information)

        if using_python_2():
            self.assertEqual("<type 'exceptions.Exception'>",
                             error_information['type'])
        else:
            self.assertEqual("<class 'Exception'>", error_information['type'])

        self.assertEqual('I died!', error_information['exception'])
        self.assertIsNotNone(error_information['traceback'])

    def _foundations_deserialize(self, serialized_value):
        from foundations_internal.foundations_serializer import deserialize
        return deserialize(serialized_value)