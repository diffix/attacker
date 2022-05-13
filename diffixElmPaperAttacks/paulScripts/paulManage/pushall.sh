#!/bin/bash

# $1 is the file name

scp -i ../.ssh/id_rsa_root $1 root@paul01:$2
scp -i ../.ssh/id_rsa_root $1 root@paul02:$2
scp -i ../.ssh/id_rsa_root $1 root@paul03:$2
scp -i ../.ssh/id_rsa_root $1 root@paul04:$2
scp -i ../.ssh/id_rsa_root $1 root@paul05:$2
scp -i ../.ssh/id_rsa_root $1 root@paul06:$2
scp -i ../.ssh/id_rsa_root $1 root@paul07:$2
scp -i ../.ssh/id_rsa_root $1 root@paul08:$2
scp -i ../.ssh/id_rsa_root $1 root@paul09:$2
