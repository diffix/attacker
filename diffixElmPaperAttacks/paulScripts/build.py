
hosts = [ 'pinky07',
          'pinky08',
          'pinky09',
          'pinky10',
          'pinky11'
]

login = 'francis'
key = 'id_rsa_root'

# Build basic execution script
# echo 'paul01'
# ssh -i ../.ssh/id_rsa_root root@paul01 $1
with open('exall.sh', 'w') as f:
    for host in hosts:
        f.write(f"echo '{host}'\n")
        f.write(f"ssh -i ~/.ssh/{key} {login}@{host} $1\n")