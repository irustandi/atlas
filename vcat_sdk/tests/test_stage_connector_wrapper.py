"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

import unittest

import vcat_sdk_fixtures.stage_connector_wrapper_fixtures as scf
import vcat_sdk_helpers.stage_connector_wrapper_helpers as sch

class TestStageConnectorWrapper(unittest.TestCase):
    def setUp(self):
        self.dummy_pipeline = scf.make_dummy_pipeline()

    def test_random_search_empty_params_dict_zero_iterations(self):
        self.assertEqual({}, self.dummy_pipeline.random_search({}, max_iterations=0))

    def test_random_search_non_empty_params_dict_zero_iterations(self):
        self.assertEqual({}, self.dummy_pipeline.random_search(scf.params_ranges_dict, max_iterations=0))

    def test_random_search_empty_params_dict_one_iteration(self):
        deployments = self.dummy_pipeline.random_search({}, max_iterations=1)

        self.assertEqual(len(deployments), 1)

        all_results = sch.get_results_list(deployments)
        self.assertEqual([{}], all_results)

    def test_random_search_simple_params_dict_one_iteration(self):
        deployments = self.dummy_pipeline.random_search(scf.simple_param_set, max_iterations=1)

        self.assertEqual(len(deployments), 1)

        all_results = sch.get_results_list(deployments)
        self.assertEqual([{'a': 1}], all_results)

    def test_random_search_simple_params_dict_two_iterations(self):
        deployments = self.dummy_pipeline.random_search(scf.simple_param_set, max_iterations=2)

        self.assertEqual(len(deployments), 2)

        all_results = sch.get_results_list(deployments)
        self.assertEqual([{'a': 1}] * 2, all_results)

    def test_random_search_less_simple_param_set_two_iterations(self):
        deployments = self.dummy_pipeline.random_search(scf.less_simple_param_set, max_iterations=2)

        self.assertEqual(len(deployments), 2)

        for result in sch.get_results_list(deployments):
            self.assertIn(result['a'], [1, 2])

    def test_random_search_more_complex_param_set_twenty_iterations(self):
        deployments = self.dummy_pipeline.random_search(scf.params_ranges_dict, max_iterations=20)

        self.assertEqual(len(deployments), 20)

        for result in sch.get_results_list(deployments):
            self.assertIn(result['param_0'], [1, 2])
            self.assertIn(result['param_1'], [3])
            self.assertIn(result['param_2'], [4, 5, 6, 7])

    def test_grid_search_empty_params_dict_zero_iterations(self):
        self.assertEqual({}, self.dummy_pipeline.grid_search({}, max_iterations=0))

    def test_grid_search_empty_params_dict_no_max_iterations(self):
        self.assertEqual({}, self.dummy_pipeline.grid_search({}))

    def test_grid_search_simple_params_dict_zero_iterations(self):
        self.assertEqual({}, self.dummy_pipeline.grid_search(scf.simple_param_set, max_iterations=0))

    def test_grid_search_simple_params_dict_one_iteration(self):
        deployments = self.dummy_pipeline.grid_search(scf.simple_param_set, max_iterations=1)

        self.assertEqual(len(deployments), 1)

        all_results = sch.get_results_list(deployments)
        self.assertEqual([{'a': 1}], all_results)

    def test_grid_search_simple_params_dict_two_iterations(self):
        deployments = self.dummy_pipeline.grid_search(scf.simple_param_set, max_iterations=2)

        self.assertEqual(len(deployments), 1) # will not do same hyperparam set twice

        all_results = sch.get_results_list(deployments)
        self.assertEqual([{'a': 1}], all_results)

    def test_grid_search_less_simple_param_set_two_iterations(self):
        deployments = self.dummy_pipeline.grid_search(scf.less_simple_param_set, max_iterations=2)

        self.assertEqual(len(deployments), 2)

        all_results = sch.get_sorted_results_items_list(deployments)
        self.assertEqual([[('a', 1)], [('a', 2)]], all_results)

    def test_grid_search_less_simple_param_set_ten_iterations(self):
        deployments = self.dummy_pipeline.grid_search(scf.less_simple_param_set, max_iterations=10)

        self.assertEqual(len(deployments), 2)

        all_results = sch.get_sorted_results_items_list(deployments)
        self.assertEqual([[('a', 1)], [('a', 2)]], all_results)

    def test_grid_search_less_simple_param_set_one_iteration(self):
        deployments = self.dummy_pipeline.grid_search(scf.less_simple_param_set, max_iterations=1)

        self.assertEqual(len(deployments), 1)

        all_results = sch.get_sorted_results_items_list(deployments)
        self.assertEqual([[('a', 1)]], all_results)

    def test_grid_search_more_complex_param_set_all_iterations(self):
        deployments = self.dummy_pipeline.grid_search(scf.params_ranges_dict)

        self.assertEqual(len(deployments), 8)

        expected_results = sch.params_cart_prod([1, 2], [3], [4, 5, 6, 7])
        expected_results.sort()

        all_results = sch.get_sorted_results_items_list(deployments)
        self.assertEqual(expected_results, all_results)

    def test_grid_search_more_complex_param_set_five_out_of_eight_iterations(self):
        deployments = self.dummy_pipeline.grid_search(scf.params_ranges_dict, max_iterations=5)

        self.assertEqual(len(deployments), 5)

        all_results = sch.get_sorted_results_items_list(deployments)

        expected_results = sch.params_cart_prod([1, 2], [3], [4, 5, 6, 7])

        expected_results = expected_results[0:5]
        expected_results.sort()

        self.assertEqual(expected_results, all_results)

    def test_adaptive_search_no_initial_params_bad_generator_function(self):
        self.dummy_pipeline.adaptive_search([], scf.bad_params_generator)

        self.assertEqual(self.dummy_pipeline.params_run, [])

    def test_adaptive_search_one_initial_param_set_dead_end(self):
        self.dummy_pipeline.adaptive_search([{'a': 1}], scf.dead_end)

        self.assertEqual(self.dummy_pipeline.params_run, [{'a': 1}])

    def test_adaptive_search_one_initial_param_but_twice_dead_end(self):
        self.dummy_pipeline.adaptive_search([{'a': 1}, {'a': 1}], scf.dead_end)

        self.assertEqual(self.dummy_pipeline.params_run, [{'a': 1}] * 2)

    def test_adaptive_search_two_initial_params_dead_end(self):
        self.dummy_pipeline.adaptive_search([{'a': 1}, {'a': 2}], scf.dead_end)

        self.assertEqual(self.dummy_pipeline.params_run, [{'a': 1}, {'a': 2}])

    def test_adaptive_search_one_initial_param_good_generator(self):
        self.dummy_pipeline.adaptive_search([{'a': 1, 'b': 2}], scf.good_generator)

        expected_results = [
            {'a': 1, 'b': 2},
            {'a': 3, 'b': 3},
            {'a': 2, 'b': 2},
            {'a': 4, 'b': 3},
            {'a': 3, 'b': 2}
        ]

        expected_results = sch.make_list_of_dicts_comparable(expected_results)

        self.assertEqual(sch.make_list_of_dicts_comparable(self.dummy_pipeline.params_run), expected_results)

    def test_adaptive_search_two_initial_params_good_generator(self):
        self.dummy_pipeline.adaptive_search([{'a': 1, 'b': 2}, {'a': 0, 'b': 3}], scf.good_generator)

        expected_results = [
            {'a': 1, 'b': 2},
            {'a': 0, 'b': 3},
            {'a': 3, 'b': 3},
            {'a': 2, 'b': 2},
            {'a': 2, 'b': 4},
            {'a': 1, 'b': 3},
            {'a': 4, 'b': 3},
            {'a': 3, 'b': 2},
            {'a': 3, 'b': 4},
            {'a': 2, 'b': 3}
        ]

        expected_results = sch.make_list_of_dicts_comparable(expected_results)

        self.assertEqual(sch.make_list_of_dicts_comparable(self.dummy_pipeline.params_run), expected_results)