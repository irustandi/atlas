"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

class ProjectsController(object):
    
    def index(self):
        from foundations_core_rest_api_components.v1.models.project import Project
        from foundations_core_rest_api_components.response import Response

        projects_future = Project.all().only(['name', 'created_at', 'owner'])
        return Response('Projects', projects_future)