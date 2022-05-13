#!/bin/bash

# $1 is the file name

scp -r -i ../.ssh/id_rsa_root $1 root@paul01:$2
