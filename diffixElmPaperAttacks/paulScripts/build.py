import os
from pathlib import Path
filePath = os.path.abspath(__file__)
parDir = os.path.abspath(os.path.join(filePath, os.pardir, os.pardir))
sys.path.append(parDir)
import rpycTools.pool

# Get hosts and ports from rpycTools.pool
pm = rpycTools.pool.pool()
hosts = pm.getHostList()
ports = pm.getPortList()

login = 'francis'
key = 'id_rsa_root'
localStorage = '/local/francis'
fileSystemMachine = 'contact'

# Build basic execution script
# echo 'paul01'
# ssh -i ../.ssh/id_rsa_root root@paul01 $1
with open('exall.sh', 'w') as f:
    f.write("echo $1\n")
    for host in hosts:
        f.write(f"echo '{host}'\n")
        f.write(f"ssh -i ~/.ssh/{key} {login}@{host} $1\n")
os.system('chmod 777 exall.sh')

# Build script to use when a new host is added
with open('newHost.sh', 'w') as f:
    f.write("./exall.sh 'mkdir /local/francis'\n")
    f.write("./exall.sh 'mkdir .venv'\n")
    f.write("./exall.sh 'python3 -m venv ~/.venv'\n")
    f.write("./exall.sh 'source .venv/bin/activate'\n")
    f.write("./exall.sh 'python3 -m pip install rpyc'\n")
os.system('chmod 777 newHost.sh')

# Script to start RPYC nodes
with open('startRpyc.sh', 'w') as f:
    f.write("source .venv/bin/activate\n")
    for port in ports:
        f.write(f"nohup rpyc_classic.py --host 0.0.0.0 --port {port} &> {localStorage}/{port}.txt & \n")
    f.write("echo done\n")
    f.write("exit 0\n")
os.system('chmod 777 startRpyc.sh')

# Script to kill RPYC nodes
with open('killRpyc.sh', 'w') as f:
    f.write("kill -9 $(pgrep -f rpyc_classic.py) \n")
os.system('chmod 777 killRpyc.sh')

# Move the start and kill scripts over to the distributed file system (via contact)
os.system(f"scp startRpyc.sh {login}@{fileSystemMachine}:")
os.system(f"scp killRpyc.sh {login}@{fileSystemMachine}:")

# Script to restart RPYC nodes
with open('restart.sh', 'w') as f:
    f.write("./exall.sh './killRpyc.sh'\n")
    f.write("./exall.sh './startRpyc.sh'\n")
os.system('chmod 777 restart.sh')