#!/bin/bash

sudo mkdir /root/.ssh
sudo cp .ssh/authorized_keys /root/.ssh/
sudo chown root:root /root/.ssh/authorized_keys
