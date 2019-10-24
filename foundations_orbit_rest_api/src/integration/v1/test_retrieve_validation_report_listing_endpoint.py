"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Susan Davis <s.davis@dessa.com>, 11 2018
"""

from foundations_spec import *

from foundations_orbit_rest_api.global_state import app_manager

class TestRetrieveValidationReportListingEndpoint(Spec):
    client = app_manager.app().test_client()
    url = '/api/v1/projects/test_project/validation_report_list'

    @let
    def redis(self):
        from foundations_contrib.global_state import redis_connection
        return redis_connection

    @set_up
    def set_up(self):
        self.redis.flushall()

    def _get_from_route(self):
        import json

        response = self.client.get(self.url)
        response_data = response.data.decode()
        return json.loads(response_data)

    def test_retrieve_validation_report_listing_gets_stored_metrics_from_redis(self):
        expected_data = [
            {
                'inference_period': '2019-02-01',
                'monitor_package': 'model_one',
                'data_contract': 'data_contract_1',
                'num_critical_tests': 1
            },
            {
                'inference_period': '2019-02-01',
                'monitor_package': 'model_one',
                'data_contract': 'data_contract_2',
                'num_critical_tests': 2
            },
            {
                'inference_period': '2019-02-02',
                'monitor_package': 'model_one',
                'data_contract': 'data_contract_1',
                'num_critical_tests': 3
            },
            {
                'inference_period': '2019-02-02',
                'monitor_package': 'model_two',
                'data_contract': 'data_contract_1',
                'num_critical_tests': 4
            },
            {
                'inference_period': '2019-02-02',
                'monitor_package': 'model_two',
                'data_contract': 'data_contract_2',
                'num_critical_tests': 5
            },
            {
                'inference_period': '2019-02-05',
                'monitor_package': 'model_one',
                'data_contract': 'data_contract_2',
                'num_critical_tests': 6
            }
        ]

        for listing_entry in expected_data:
            contract_name = listing_entry['data_contract']
            inference_period = listing_entry['inference_period']
            monitor_package = listing_entry['monitor_package']
            num_critical_tests = listing_entry['num_critical_tests']
            self.redis.hset(f'projects:test_project:monitors:{monitor_package}:validation:{contract_name}', inference_period, 'dummy')
            self.redis.hset(f'projects:test_project:monitors:{monitor_package}:validation:{contract_name}:summary', inference_period, num_critical_tests)

        data = self._get_from_route()

        self.assertEqual(expected_data, data)
