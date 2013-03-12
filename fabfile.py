import os
from fabric.api import task, run, env, cd, settings
from fabtools.vagrant import ssh_config, _settings_dict
import fabtools  # NOQA
from fabtools import files
from fabtools import require

import requests

VIRTUALHOST_TPL = """
{{default aliases=[] }}
{{default allow_override=None }}
<VirtualHost *:80>
    ServerName {{hostname}}
    {{for a in aliases}}
    ServerAlias {{a}}
    {{endfor}}

    DocumentRoot {{document_root}}

    <Directory {{document_root}}>
        Options Indexes FollowSymLinks MultiViews

        {{if allow_override}}
        AllowOverride {{allow_override}}
        {{else}}
        AllowOverride All
        {{endif}}

        Order allow,deny
        allow from all
    </Directory>
</VirtualHost>
"""


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'

    env['mysql_user'] = 'root'
    env['mysql_password'] = os.environ.get('MYSQL_PASSWORD', 'password')


@task
def prod():
    env['user'] = 'root'
    env['hosts'] = ['server_ip_or_domain.tld']
    env['port'] = '22'

    env['mysql_user'] = 'root'
    env['mysql_password'] = os.environ.get('MYSQL_PASSWORD', 'password')


@task
def config():
    env['owncloud'] = {
        'unix_user': 'owncloud',
        'url': 'cloud.domain.tld',
        'url_aliases': [],

        'database_name': 'owncloud',
        'database_user': 'owncloud',
        'database_password': os.environ.get('OWNCLOUD_MYSQL_PASSWORD', 'password'),

        'admin_user': 'admin',
        'admin_password': os.environ.get('OWNCLOUD_ADMIN_PASSWORD', 'password'),
    }


def _add_user(*args, **kwargs):

    require.user(*args, **kwargs)
    if 'name' not in kwargs:
        user = args[0]
    else:
        user = kwargs['name']

    if not fabtools.files.is_file('/home/%s/.ssh/authorized_keys' % user):
        run('mkdir -p /home/%s/.ssh/' % user)
        run('cp /root/.ssh/authorized_keys /home/%s/.ssh/' % user)
        run('chown %(user)s:%(user)s /home/%(user)s/.ssh/ -R' % {'user': user})


@task
def install():
    fabtools.require.system.locale('fr_FR.UTF-8')

    fabtools.deb.update_index()
    fabtools.deb.preseed_package('mysql-server', {
        'mysql-server/root_password': ('password', env['mysql_password']),
        'mysql-server/root_password_again': ('password', env['mysql_password']),
    })
    require.deb.packages([
        'locales',
        'apache2',
        'mysql-server',
        'mysql-client',
        'php5',
        'php5-mysql',
        'php5-gd',
        'libapache2-mod-php5'
    ])

    _add_user(
        name=env['owncloud']['unix_user'],
        password=None,
        shell='/bin/bash'
    )

    require.mysql.user(env['owncloud']['database_user'], env['owncloud']['database_password'])
    require.mysql.database(env['owncloud']['database_name'], owner=env['owncloud']['database_user'])
    require.directory('/home/%s/prod/' % env['owncloud']['unix_user'])

    if not files.is_dir('/home/%s/prod/www/' % env['owncloud']['unix_user']):
        run(
            'chown %(unix_user)s:%(unix_user)s /home/%(unix_user)s/prod/'
            % {
                'unix_user': env['owncloud']['unix_user']
            }
        )

        with settings(user=env['owncloud']['unix_user']):
            with cd('/home/%s/prod/' % env['owncloud']['unix_user']):
                require.file(url='http://mirrors.owncloud.org/releases/owncloud-4.5.7.tar.bz2')
                run('tar xjf owncloud-4.5.7.tar.bz2')
                run('mv owncloud www')
                run('rm owncloud-4.5.7.tar.bz2')

        with cd('/home/%s/prod/' % env['owncloud']['unix_user']):
            run('chown %s:www-data www/ -R' % env['owncloud']['unix_user'])
            run('chmod ug+rwX www/ -R')
            run('chmod ugo+rwX www/config -R')

    run("a2enmod rewrite")
    run('rm -f /etc/apache2/sites-enabled/000-default')
    require.apache.site(
        env['owncloud']['url'],
        template_contents=VIRTUALHOST_TPL,
        hostname=env['owncloud']['url'],
        document_root='/home/%s/prod/www/' % env['owncloud']['unix_user'],
        enable=True
    )
    fabtools.apache.restart()

    s = requests.Session()
    s.post(
        'http://%s/index.php' % env['owncloud']['url'],
        data={
            'install': 'true',
            'adminlogin': env['owncloud']['admin_user'],
            'adminpass': env['owncloud']['admin_password'],
            'directory': '/home/%s/prod/www/data' % env['owncloud']['unix_user'],
            'dbtype': 'mysql',
            'dbuser': env['owncloud']['database_user'],
            'dbpass': env['owncloud']['database_password'],
            'dbname': env['owncloud']['database_name'],
            'dbhost': 'localhost'
        }
    )


@task
def uninstall():
    fabtools.mysql.drop_database(env['owncloud']['database_name'])
    fabtools.mysql.drop_user(env['owncloud']['database_user'])
    run('rm -rf /home/%s/prod/' % env['owncloud']['unix_user'])
    fabtools.apache.disable_site(env['owncloud']['url'])
    fabtools.apache.restart()
