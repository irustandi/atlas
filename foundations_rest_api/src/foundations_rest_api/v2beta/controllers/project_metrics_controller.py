"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

from foundations_rest_api.utils.api_resource import api_resource

from foundations_core_rest_api_components.lazy_result import LazyResult
from foundations_core_rest_api_components.response import Response

from collections import namedtuple

@api_resource('/api/v2beta/projects/<string:project_name>/overview_metrics')
class ProjectMetricsController(object):

    def index(self):
        return Response('Jobs', LazyResult(self._get_metrics))

    def _get_metrics(self):
        from foundations_contrib.global_state import redis_connection
        from foundations_internal.fast_serializer import deserialize
        from collections import defaultdict

        project_key = f'projects:{self._project_name()}:metrics'
        serialized_project_metrics = redis_connection.hgetall(project_key)
        project_metrics = []
        for metric_key, serialized_metric in serialized_project_metrics.items():
            job_id, metric_name = metric_key.decode().split(':')
            timestamp, value = deserialize(serialized_metric)
            project_metrics.append({
                'job_id': job_id,
                'metric_name': metric_name,
                'timestamp': timestamp,
                'value': value
            })
        project_metrics = sorted(project_metrics, key=lambda item: item['timestamp'])
        grouped_metrics = defaultdict(list)
        for metric in project_metrics:
            grouped_metrics[metric['metric_name']].append([metric['job_id'], metric['value']])
        result = []
        for metric_key, metrics in grouped_metrics.items():
            result.append({
                'metric_name': metric_key,
                'values': metrics
            })
        return result

    def _project_name(self):
        return self.params['project_name']