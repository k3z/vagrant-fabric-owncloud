==========================
Vagrant + fabric bootstrap
==========================

Prerequisites
=============

On Ubuntu 12.10
---------------

Prerequisites :

.. code-block:: sh

    $ sudo apt-get install virtualbox rubygem1.8
    $ gem install vagrant


Quickstart
==========

Install Python dependencies (fabric…) with *buildout* :

.. code-block:: sh

    $ python bootstrap.py
    $ bin/buildout


Install `vagrant-hostmaster <https://github.com/mosaicxm/vagrant-hostmaster>`_ :

.. code-block:: sh

    $ vagrant gem install vagrant-hostmaster

.. Note::

    `vagrant-hostmaster <https://github.com/mosaicxm/vagrant-hostmaster>`_ is a Vagrant plugin to 
    manage ``/etc/hosts`` entries on both the host OS **and** guest VMs.

    You can configure the hostname with this line in your ``Vagrantfile``

    ::

        config.vm.host_name = "vagrant.example.com"
        config.hosts.name = "vagrant.example.com"
        config.hosts.aliases = "example.com"

Download and start *vagrant* VM :

.. code-block:: sh

    $ vagrant up

You can test *ping* command on hostname configured by *vagrant-hostmaster* :

.. code-block:: sh

    $ ping example.com
    PING example.com (192.168.33.10): 56 data bytes
    64 bytes from 192.168.33.10: icmp_seq=0 ttl=64 time=0.383 ms
    64 bytes from 192.168.33.10: icmp_seq=1 ttl=64 time=0.462 ms

Execute *fabric* install :

.. code-block:: sh

    $ bin/fab vagrant install
    [127.0.0.1] Executing task 'install'
    [127.0.0.1] run: whoami
    [127.0.0.1] out: root
    [127.0.0.1] out: 

Notes
=====

In ``Vagrantfile`` have set mac address :
 
::

    config.vm.network :hostonly, "192.168.33.10", :mac => "080027e5f699"

It's important to not modify this mac address otherwise second interface will be set on ``eth2`` by
udev, and you will not be able to ping from your Host to your Guest.
