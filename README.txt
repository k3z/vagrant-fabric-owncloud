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


Quickstart
==========

Install Python dependencies (fabric…) with *buildout* :

.. code-block:: sh

    $ python bootstrap.py
    $ bin/buildout

Download and start *vagrant* VM :

.. code-block:: sh

    $ vagrant up

Execute *fabric* install :

.. code-block:: sh

    $ bin/fab vagrant install
    [127.0.0.1] Executing task 'install'
    [127.0.0.1] run: whoami
    [127.0.0.1] out: root
    [127.0.0.1] out: 

