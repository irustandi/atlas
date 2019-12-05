"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

from foundations_spec import *

class TestBundleDeployment(Spec):

    @let
    def job_name(self):
        return self.faker.uuid4()

    @let_now
    def config_manager(self):
        from foundations_contrib.config_manager import ConfigManager
        return self.patch('foundations_contrib.global_state.config_manager', ConfigManager())

    def test_job_bundle_returns_job_bundler_with_correct_params(self):
        from foundations_local_docker_scheduler_plugin.bundle_deployment import job_bundle

        mock_job_bundler_class = self.patch('foundations_contrib.job_bundler.JobBundler', ConditionalReturn())

        mock_empty_job_class = self.patch('foundations_contrib.job_bundling.empty_job.EmptyJob')
        mock_empty_job = Mock()
        mock_empty_job_class.return_value = mock_empty_job

        mock_folder_job_source_bundle_class = self.patch('foundations_contrib.job_bundling.folder_job_source_bundle.FolderJobSourceBundle')
        mock_folder_job_source_bundle = Mock()
        mock_folder_job_source_bundle_class.return_value = mock_folder_job_source_bundle

        mock_config_method = self.patch('foundations_contrib.global_state.config_manager.config')
        mock_config = Mock()
        mock_config_method.return_value = mock_config

        mock_job_bundler = Mock()
        mock_job_bundler_class.return_when(mock_job_bundler, self.job_name, mock_config, mock_empty_job, mock_folder_job_source_bundle, 'job_source')

        self.assertEqual(mock_job_bundler, job_bundle(self.job_name))

    def test_submit_job_bundle_posts_to_correct_endpoint_with_file(self):
        from foundations_local_docker_scheduler_plugin.bundle_deployment import submit_job_bundle
        from foundations_contrib.job_bundling.folder_job_source_bundle import FolderJobSourceBundle

        self.config_manager['scheduler_url'] = 'http://localhost:5000'

        folder_job_bundle = FolderJobSourceBundle()

        mock_open = self.patch('builtins.open', ConditionalReturn())
        mock_file = Mock()
        mock_open.return_when(mock_file, '.', 'rb')
        mock_file.__enter__ = lambda *_: mock_file
        mock_file.__exit__ = Mock()

        mock_post = self.patch('requests.post', ConditionalReturn())
        mock_response = Mock()
        mock_post.return_when(mock_response, 'http://localhost:5000/job_bundle', files={'job_bundle': mock_file})

        response = submit_job_bundle(folder_job_bundle)

        self.assertEqual(mock_response, response)