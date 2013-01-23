from fabric.api import task, run, env
from fabtools.vagrant import ssh_config, _settings_dict
import fabtools  # NOQA


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'


@task
def install():
    run('whoami')
