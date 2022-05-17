This directory contains scripts used to manage execution of rpyc on a cluster.

The scripts are very specific to the clusters at MPI-SWS.

Upon first login, do `. dokey.sh`

If host list changes:

mkdir .venv

python3 -m venv ~/.venv

source .venv/bin/activate

python3 -m pip install rpyc

mkdir /local/francis

rpyc_classic.py

