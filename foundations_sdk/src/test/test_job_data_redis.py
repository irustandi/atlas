"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

import unittest
import json
import fakeredis
from mock import patch
import six

from foundations.job_data_redis import JobDataRedis
from foundations.redis_pipeline_wrapper import RedisPipelineWrapper
from foundations.global_state import redis_connection


class TestJobDataRedis(unittest.TestCase):

    def setUp(self):
        self._redis = fakeredis.FakeStrictRedis()

    def _set_redis(self, job_id, parameter, data):
        self._redis.set('jobs:{}:{}'.format(job_id, parameter), data)

    def _sadd_redis(self, job_id, parameter, data):
        self._redis.sadd('jobs:{}:{}'.format(job_id, parameter), data)

    def _load_data_new_job(self, job_id, data):
        set_parameter_name = ['project', 'start_time',
                              'completed_time', 'user', 'state']
        sadd_parameter_name = ['parameters', 'input_parameters', 'metrics']

        for key, value in data.items():
            if key in set_parameter_name:
                self._set_redis(job_id, key, value)
            if key in sadd_parameter_name:
                self._sadd_redis(job_id, key, value)

    def _sadd_redis_project_name(self, project_name, job_id):
        self._redis.sadd(
            'project:{}:jobs:running'.format(project_name), job_id)

    def test_get_job_data_gets_data(self):
        data = {
            'project': 'banana',
            'user': 'potter',
            'parameters': json.dumps({'harry': 'potter'}),
            'input_parameters': json.dumps({'ron': 'weasley'}),
            'metrics': json.dumps(('123', 'hermione', 'granger')),
            'state': 'dead',
            'start_time': '456',
            'completed_time': '123'
        }
        job_id = 'the boy who lived'
        redis_pipe = RedisPipelineWrapper(
            self._redis.pipeline())
        job_data = JobDataRedis(redis_pipe, job_id)
        self._load_data_new_job(job_id, data)

        result = job_data.get_job_data()
        redis_pipe.execute()
        expected_result = {
            'project_name': 'banana',
            'job_id': job_id,
            'user': 'potter',
            'job_parameters': [{'harry': 'potter'}],
            'input_params': [{'ron': 'weasley'}],
            'output_metrics': [['123', 'hermione', 'granger']],
            'status': 'dead',
            'start_time': '456',
            'completed_time': '123'
        }
        self.assertDictEqual(expected_result, result.get())

    def test_get_job_data_gets_data_different_data(self):
        data = {
            'project': 'apple',
            'user': 'potter',
            'parameters': json.dumps({'ron': 'potter'}),
            'input_parameters': json.dumps({'harry': 'weasley'}),
            'metrics': json.dumps(('123', 'hermione', 'granger')),
            'state': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }
        job_id = 'sushine'
        redis_pipe = RedisPipelineWrapper(
            self._redis.pipeline())
        job_data = JobDataRedis(redis_pipe, job_id)
        self._load_data_new_job(job_id, data)

        result = job_data.get_job_data()
        redis_pipe.execute()

        expected_result = {
            'project_name': 'apple',
            'job_id': job_id,
            'user': 'potter',
            'job_parameters': [{'ron': 'potter'}],
            'input_params': [{'harry': 'weasley'}],
            'output_metrics': [['123', 'hermione', 'granger']],
            'status': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }

        self.assertDictEqual(expected_result, result.get())

    def test_get_job_data_all_jobs_single_job(self):
        project_name = 'apple'
        data = {
            'project': project_name,
            'user': 'potter',
            'parameters': json.dumps({'ron': 'potter'}),
            'input_parameters': json.dumps({'harry': 'weasley'}),
            'metrics': json.dumps(('123', 'hermione', 'granger')),
            'state': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }
        job_id_1 = 'sushine'

        self._sadd_redis_project_name(project_name, job_id_1)
        self._load_data_new_job(job_id_1, data)

        expected_result_1 = {
            'project_name': project_name,
            'job_id': job_id_1,
            'user': 'potter',
            'job_parameters': [{'ron': 'potter'}],
            'input_params': [{'harry': 'weasley'}],
            'output_metrics': [['123', 'hermione', 'granger']],
            'status': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }

        results = JobDataRedis.get_all_jobs_data(
            project_name, self._redis)

        self.assertDictEqual(results[0], expected_result_1)

    def test_get_job_data_all_jobs_single_job_different_data(self):
        project_name = 'pomme'
        data = {
            'project': project_name,
            'user': 'baker',
            'parameters': json.dumps({'ron': 'potter'}),
            'input_parameters': json.dumps({'harry': 'weasley'}),
            'metrics': json.dumps(('123', 'hermione', 'granger')),
            'state': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }
        job_id_1 = 'sushine'

        self._sadd_redis_project_name(project_name, job_id_1)
        self._load_data_new_job(job_id_1, data)

        expected_result_1 = {
            'project_name': project_name,
            'job_id': job_id_1,
            'user': 'baker',
            'job_parameters': [{'ron': 'potter'}],
            'input_params': [{'harry': 'weasley'}],
            'output_metrics': [['123', 'hermione', 'granger']],
            'status': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }

        results = JobDataRedis.get_all_jobs_data(
            project_name, self._redis)

        self.assertDictEqual(results[0], expected_result_1)

    def test_get_job_data_all_jobs_two_jobs(self):
        project_name = 'apple'
        data = {
            'project': project_name,
            'user': 'potter',
            'parameters': json.dumps({'ron': 'potter'}),
            'input_parameters': json.dumps({'harry': 'weasley'}),
            'metrics': json.dumps(('123', 'hermione', 'granger')),
            'state': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }
        job_id_1 = 'sushine'
        job_id_2 = 'rain'

        self._sadd_redis_project_name(project_name, job_id_1)
        self._sadd_redis_project_name(project_name, job_id_2)
        self._load_data_new_job(job_id_1, data)
        self._load_data_new_job(job_id_2, data)

        expected_result_1 = {
            'project_name': project_name,
            'job_id': job_id_1,
            'user': 'potter',
            'job_parameters': [{'ron': 'potter'}],
            'input_params': [{'harry': 'weasley'}],
            'output_metrics': [['123', 'hermione', 'granger']],
            'status': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }

        expected_result_2 = {
            'project_name': project_name,
            'job_id': job_id_2,
            'user': 'potter',
            'job_parameters': [{'ron': 'potter'}],
            'input_params': [{'harry': 'weasley'}],
            'output_metrics': [['123', 'hermione', 'granger']],
            'status': 'completed',
            'start_time': '1231003123',
            'completed_time': '123'
        }

        results = JobDataRedis.get_all_jobs_data(
            project_name, self._redis)

        six.assertCountEqual(self,
                             results, [expected_result_1, expected_result_2])
