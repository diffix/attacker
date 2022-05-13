#!/bin/bash

# $1 is the file name

scp -i ../.ssh/id_rsa_root root@paul01:$1 $2
