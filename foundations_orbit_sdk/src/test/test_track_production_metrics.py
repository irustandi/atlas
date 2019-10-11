"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

from foundations_spec import *
from foundations_orbit import track_production_metrics
import fakeredis
import pickle

class TestTrackProductionMetrics(Spec):

    mock_redis = let_patch_mock('foundations_contrib.global_state.redis_connection', fakeredis.FakeRedis())
    mock_int_like = let_mock()
    mock_float_like = let_mock()

    @let_now
    def mock_environment(self):
        return self.patch('os.environ', {})

    @let
    def monitor_name(self):
        return self.faker.uuid4()

    @let
    def project_name(self):
        return self.faker.word()

    @let
    def metric_name(self):
        return self.faker.word()

    @let
    def column_name(self):
        return self.faker.word()

    @let
    def column_value(self):
        return self.faker.random.random()

    @let
    def column_name_2(self):
        return self.faker.word()

    @let
    def column_value_2(self):
        return self.faker.random.random()

    @let
    def numpy_int32(self):
        import numpy
        return numpy.int32(self.faker.random.randint(0, 100))

    @let
    def numpy_int64(self):
        import numpy
        return numpy.int64(self.faker.random.randint(0, 100))

    @let
    def numpy_float32(self):
        import numpy
        return numpy.float32(self.faker.random.random())

    @let
    def numpy_float64(self):
        import numpy
        return numpy.float64(self.faker.random.random())

    @let
    def int_value(self):
        return self.faker.random.randint(1, 100)

    @let
    def dataframe(self):
        import pandas
        return pandas.DataFrame()

    @set_up
    def set_up(self):
        self.mock_environment['MONITOR_NAME'] = self.monitor_name
        self.mock_environment['PROJECT_NAME'] = self.project_name
        
        self.mock_int_like.__int__ = lambda *args: self.int_value
        self.mock_float_like.__float__ = lambda *args: self.column_value


    @tear_down
    def tear_down(self):
        self.mock_redis.flushall()

    def test_track_production_metrics_can_track_empty_metric(self):
        track_production_metrics(self.metric_name, {})
        production_metrics = self._retrieve_tracked_metrics()
        self.assertEqual({self.metric_name: []}, production_metrics)

    def test_track_production_metrics_with_nonexistent_monitor_name_throws_exception(self):
        self.mock_environment['MONITOR_NAME'] = ''
    
        with self.assertRaises(RuntimeError) as error_context:
            track_production_metrics(self.metric_name, {})
        
        self.assertIn('Monitor name not set', error_context.exception.args)

    def test_track_production_metrics_with_nonexistent_project_name_throws_exception(self):
        self.mock_environment['PROJECT_NAME'] = ''
    
        with self.assertRaises(RuntimeError) as error_context:
            track_production_metrics(self.metric_name, {})
        
        self.assertIn('Project name not set', error_context.exception.args)

    def test_track_production_metrics_can_log_a_metric(self):
        track_production_metrics(self.metric_name, {self.column_name: self.column_value})
        production_metrics = self._retrieve_tracked_metrics()
        self.assertEqual({self.metric_name: [(self.column_name, self.column_value)]}, production_metrics)   

    def test_track_production_metrics_can_log_multiple_metrics_values_in_one_call(self):
        track_production_metrics(self.metric_name, {self.column_name: self.column_value, self.column_name_2: self.column_value_2})
        
        production_metrics = self._retrieve_tracked_metrics()
        production_metrics[self.metric_name].sort(key=lambda entry: entry[0])

        expected_metrics = {self.metric_name: [(self.column_name, self.column_value), (self.column_name_2, self.column_value_2)]}
        expected_metrics[self.metric_name].sort(key=lambda entry: entry[0])

        self.assertEqual(expected_metrics, production_metrics)   
        
    def test_track_production_metrics_can_log_multiple_metrics_values_in_different_calls(self):
        track_production_metrics(self.metric_name, {self.column_name: self.column_value})
        track_production_metrics(self.metric_name, {self.column_name_2: self.column_value_2})
        
        production_metrics = self._retrieve_tracked_metrics()
        production_metrics[self.metric_name].sort(key=lambda entry: entry[0])
        
        expected_metrics = {self.metric_name: [(self.column_name, self.column_value), (self.column_name_2, self.column_value_2)]}
        expected_metrics[self.metric_name].sort(key=lambda entry: entry[0])

        self.assertEqual(expected_metrics, production_metrics)   

    def test_track_production_metrics_logs_numpy_int32_as_python_int(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_int32})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertIsInstance(metric_value, int)

    def test_track_production_metrics_logs_numpy_int32_as_python_int_preserves_value(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_int32})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertEqual(metric_value, int(self.numpy_int32))

    def test_track_production_metrics_logs_numpy_int64_as_python_int(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_int64})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertIsInstance(metric_value, int)

    def test_track_production_metrics_logs_numpy_int64_as_python_int_preserves_value(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_int64})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertEqual(metric_value, int(self.numpy_int64))

    def test_track_production_metrics_logs_numpy_float32_as_python_float(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_float32})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertIsInstance(metric_value, float)

    def test_track_production_metrics_logs_numpy_float32_as_python_float_preserves_value(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_float32})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertEqual(metric_value, float(self.numpy_float32))

    def test_track_production_metrics_logs_numpy_float64_as_python_float(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_float64})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertIsInstance(metric_value, float)

    def test_track_production_metrics_logs_numpy_float64_as_python_float_preserves_value(self):
        track_production_metrics(self.metric_name, {self.column_name: self.numpy_float64})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertEqual(metric_value, float(self.numpy_float64))

    def test_track_production_metrics_logs_int_like_as_python_int_preserves_value(self):
        track_production_metrics(self.metric_name, {self.column_name: self.mock_int_like})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertEqual(metric_value, self.int_value)

    def test_track_production_metrics_logs_float_like_as_python_float_preserves_value(self):
        track_production_metrics(self.metric_name, {self.column_name: self.mock_float_like})
        
        production_metrics = self._retrieve_tracked_metrics()
        metric_value = production_metrics[self.metric_name][0][1]

        self.assertEqual(metric_value, self.column_value)

    def test_track_production_metrics_throws_type_error_if_cannot_cast_to_float_or_int(self):
        with self.assertRaises(TypeError) as ex:
            track_production_metrics(self.metric_name, {self.column_name: self.dataframe})
        self.assertIn(f'cannot log metric `{self.metric_name}` with column name `{self.column_name}` of type `{type(self.dataframe)}` - must be able to cast to int or float', ex.exception.args)

    def _retrieve_tracked_metrics(self):
        production_metrics_from_redis = self.mock_redis.hgetall(f'projects:{self.project_name}:monitors:{self.monitor_name}:production_metrics')
        return {metric_name.decode(): pickle.loads(serialized_metrics) for metric_name, serialized_metrics in production_metrics_from_redis.items()}

