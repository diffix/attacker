import os

hosts = [ 'pinky07',
          'pinky08',
          'pinky09',
          'pinky10',
          'pinky11'
]

login = 'francis'
key = 'id_rsa_root'
localStorage = '/local/francis'

# Build basic execution script
# echo 'paul01'
# ssh -i ../.ssh/id_rsa_root root@paul01 $1
with open('exall.sh', 'w') as f:
    f.write("echo $1")
    for host in hosts:
        f.write(f"echo '{host}'\n")
        f.write(f"ssh -i ~/.ssh/{key} {login}@{host} $1\n")
os.system('chmod 777 exall.sh')

# Build script to use when a new host is added
with open('newHost.sh', 'w') as f:
    f.write("./exall.sh 'mkdir .venv'\n")
    f.write("./exall.sh 'python3 -m venv ~/.venv'\n")
    f.write("./exall.sh 'source .venv/bin/activate'\n")
    f.write("./exall.sh 'python3 -m pip install rpyc'\n")
    f.write("./exall.sh 'mkdir /local/francis'\n")
os.system('chmod 777 newHost.sh')