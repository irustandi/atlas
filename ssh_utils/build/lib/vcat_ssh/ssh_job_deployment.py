from vcat.job_bundler import JobBundler


class SSHJobDeployment(object):

    def __init__(self, job_name, job, job_source_bundle):
        self._config = {}
        self._job_name = job_name
        self._job = job
        self._job_bundler = JobBundler(
            self._job_name, self._config, self._job, job_source_bundle)

    def config(self):
        return self._config

    def job_name(self):
        return self._job_name

    def deploy(self):
        self._job_bundler.bundle()
        try:
            self._deploy_internal()
        finally:
            self._job_bundler.cleanup()

    def is_job_complete(self):
        from subprocess import call
        from os import devnull

        command = self._check_job_done_ssh_command()
        return call(command, stdout=devnull) == 0

    def fetch_job_results(self):
        pass

    def _deploy_internal(self):
        from subprocess import call
        from os import devnull
        
        command = self._deploy_scp_command()
        call(command, stdout=devnull)

    def _deploy_scp_command(self):
        ssh_command = 'scp ' + self._ssh_arguments() + ' ' + self._full_archive_path() + ' ' + \
            self._user_at_host() + ':' + self._code_path()
        return self._command_in_shell_command(ssh_command)

    def _check_job_done_ssh_command(self):
        scp_command = 'ssh ' + self._ssh_arguments() + ' ' + self._user_at_host() + ' "stat ' + \
            self._result_path() + '/' + self._job_bundler.job_archive_name() + '"'
        return self._command_in_shell_command(scp_command)

    def _ssh_arguments(self):
        return '-oBatchMode=yes -i ' + self._key_path()

    def _command_in_shell_command(self, command):
        return [self._shell_command(), '--login', '-c', command]

    def _shell_command(self):
        return self._config['shell_command']

    def _full_archive_path(self):
        from os.path import abspath
        return abspath(self._job_bundler.job_archive())

    def _code_path(self):
        return self._config['code_path']

    def _result_path(self):
        return self._config['result_path']

    def _user_at_host(self):
        return self._config['remote_user'] + '@' + self._config['remote_host']

    def _key_path(self):
        return self._config['key_path']
