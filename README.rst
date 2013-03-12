======================
Owncloud deploy script
======================


vagrant-fabric-owncloud is a fabric script for testing or deploying Owncloud on Debian/Ubuntu systems.

The Fabric/Fabtools script is based on Harobeds wonderfull `vagrant-fabric-bootstrap <http://harobed.github.com/vagrant-fabric-bootstrap/>`_ script.


Testing in a Vagrant Box
------------------------

You must have Vagrant properly installed. The **vagrant-hostmaster** plugin is needed.

Prerequisites On Ubuntu 12.10
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ sudo apt-get install virtualbox rubygems1.8
    $ gem install vagrant vagrant-hostmaster


Prerequisites On Mac OS X
^^^^^^^^^^^^^^^^^^^^^^^^^

Install Vagrant ::

$ gem install vagrant vagrant-hostmaster


Get source and install dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone vagrant-fabric-owncloud project on your working computer ::

    $ git clone https://github.com/k3z/vagrant-fabric-owncloud.git


Install Python dependencies (fabric…) with buildout ::

    $ python bootstrap.py
    $ bin/buildout


Download and start vagrant VM ::

$ vagrant up

Execute fabric install
^^^^^^^^^^^^^^^^^^^^^^

::

    $ bin/fab vagrant config install

if all run well, paste this url in your browser : http://cloud.domain.tld.
And proceed to Owncloud final installation.



Deploy on your server
---------------------

Get source and install dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone vagrant-fabric-owncloud project on your working computer ::

    $ git clone https://github.com/k3z/vagrant-fabric-owncloud.git


Install Python dependencies (fabric…) with buildout ::

    $ python bootstrap.py
    $ bin/buildout


Configuration
^^^^^^^^^^^^^

open fabfile.py and change the env variables in the *prod()* and *config()* methods according to your environment.


Execute
^^^^^^^

Execute fabric script ::

    $ bin/fab prod config install

if all run well, paste the url according to your configuration. And proceed to Owncloud final installation.
