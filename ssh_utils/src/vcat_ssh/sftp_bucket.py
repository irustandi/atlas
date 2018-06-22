"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""


class SFTPBucket(object):

    def __init__(self, path):
        from pysftp import Connection
        from vcat.global_state import config_manager

        self._path = path
        self._connection = Connection(
            config_manager['remote_host'],
            config_manager['remote_user'],
            private_key=config_manager['key_path']
        )

        self._log().debug(
            'Creating connection to %s@%s using key %s at location %s',
            config_manager['remote_user'],
            config_manager['remote_host'],
            config_manager['key_path'],
            self._path
        )

    def upload_from_string(self, name, data):
        from vcat.simple_tempfile import SimpleTempfile

        self._log().debug('Uploading %s', self._full_path(name))

        with SimpleTempfile('w+b') as temp_file:
            temp_file.write_and_flush(data)
            self.upload_from_file(name, temp_file)

    def upload_from_file(self, name, input_file):
        self._log().debug('Uploading %s from %s', self._full_path(name), input_file.name)

        self._ensure_path_exists(name)
        with self.change_directory_for_name(name):
            self._connection.put(input_file.name, self._temporary_name(name))
            self._connection.rename(self._temporary_name(name), name)

    def exists(self, name):
        from os.path import basename

        self._log().debug('Checking if %s exists', self._full_path(name))

        with self.change_directory_for_name(name):
            return self._connection.exists(basename(name))

    def download_as_string(self, name):
        from vcat.simple_tempfile import SimpleTempfile
        from vcat.utils import byte_string

        self._log().debug('Downloading %s', self._full_path(name))

        with SimpleTempfile('w+b') as temp_file:
            self.download_to_file(name, temp_file)
            data_bytes = temp_file.read()
            return byte_string(data_bytes)

    def download_to_file(self, name, output_file):
        from os.path import basename

        self._log().debug('Downloading %s to %s', self._full_path(name), output_file.name)

        with self.change_directory_for_name(name):
            self._connection.get(basename(name), output_file.name)

    def list_files(self, pathname):
        from fnmatch import fnmatch

        self._log().debug('Listing files with pathname %s', self._full_path(pathname))

        with self._connection.cd(self._path):
            paths = self._connection.listdir()
            for path in paths:
                self._log().debug('Got file %s', path)
            return filter(lambda path: fnmatch(path, pathname), paths)

    def _ensure_path_exists(self, name):
        self._connection.makedirs(self._directory_path(name))

    def change_directory_for_name(self, name):
        return self._connection.cd(self._directory_path(name))

    def _temporary_name(self, name):
        return name + '.vtmpfile'

    def _directory_path(self, name):
        from os.path import dirname
        from os.path import join

        return join(self._path, dirname(name))

    def _full_path(self, name):
        from os.path import join
        return join(self._path, name)

    def _log(self):
        from vcat.global_state import log_manager
        return log_manager.get_logger(__name__)
