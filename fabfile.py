import os
from fabric.api import task, run, env, cd, settings, puts, local  #NOQA
from fabtools.vagrant import ssh_config, _settings_dict
import fabtools  # NOQA
from fabtools import files
from fabtools import require


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
        'unix_user_password': os.environ.get('USER_PASSWORD', 'password'),
        'url': 'cloud.domain.tld',
        'url_aliases': [],

        'database_name': 'owncloud',
        'database_user': 'owncloud',
        'database_password': os.environ.get('OWNCLOUD_MYSQL_PASSWORD', 'password'),

        'admin_user': 'admin',
        'admin_password': os.environ.get('OWNCLOUD_ADMIN_PASSWORD', 'password'),
        'admin_email': 'mail@domain.tld'
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
    run('whoami')

    fabtools.require.system.locale('fr_FR.UTF-8')

    fabtools.deb.update_index()
    fabtools.deb.preseed_package('mysql-server', {
        'mysql-server/root_password': ('password', env['mysql_password']),
        'mysql-server/root_password_again': ('password', env['mysql_password']),
    })
    require.deb.packages([
        'build-essential',
        'devscripts',
        'locales',
        'apache2',
        'mysql-server',
        'mysql-client',
        'php5',
        'php5-mysql',
        'php5-gd',
        'libapache2-mod-php5',
        'vim',
        'mc',
        'curl',
        'libmysqlclient-dev',
        'python-distribute'
    ])

    _add_user(
        name=env['owncloud']['unix_user'],
        password=env['owncloud']['unix_user_password'],
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

    VIRTUALHOST_FILE = '/etc/apache2/sites-available/' + env['owncloud']['url']

    require.files.template_file(
        template_contents=VIRTUALHOST_TPL,
        path=VIRTUALHOST_FILE,
        context={
            'server_name': env['owncloud']['url'],
            'port': 80,
            'document_root': '/home/%s/prod/www/' % env['owncloud']['unix_user'],
            'server_admin': env['owncloud']['admin_email'],
        },
        owner='root',
        group='root',
    )

    if not fabtools.files.is_link(VIRTUALHOST_FILE):
        run('rm -f /etc/apache2/sites-enabled/000-default')
        run("a2ensite " + env['owncloud']['url'])

    if not fabtools.files.is_link('/etc/apache2/mods-enabled/rewrite.load'):
        run("a2enmod rewrite")

    run("/etc/init.d/apache2 restart")

    #  TODO Owncloud install script


VIRTUALHOST_TPL = """
#
# Template file managed by Fabtools
#

<VirtualHost *:%(port)d>
    ServerAdmin %(server_admin)s

    DocumentRoot %(document_root)s

    ServerName %(server_name)s

    ErrorLog ${APACHE_LOG_DIR}/%(server_name)s-error_log
    CustomLog ${APACHE_LOG_DIR}/%(server_name)s-access_log common

    <Directory %(document_root)s>
        <IfModule mod_rewrite.c>
            Options +FollowSymLinks
        </IfModule>

        DirectoryIndex index.php
        AllowOverride All

        Order allow,deny
        Allow from all
    </Directory>

</VirtualHost>
"""
