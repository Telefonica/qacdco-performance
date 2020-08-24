QA CDO JMETER SLAVE DEPLOY
==========================

## Requirements:

### Injector
Deploy a fresh ubuntu virtual machine

Install native python if its not installed. New AWS machines lack python2.

Add contint public key into authorized_keys file, and as many keys as you need

### Ansible in local machine
Install native python if its not installed

Install python-pip

    $ sudo apt install python-pip --assume-yes

Install requirements

    $ pip install -r requirements.txt
    
Setup inventories into ansible/inventories/hosts

```
perf01 ansible_ssh_host=*IP* ansible_ssh_port=*PORT* 
ansible_ssh_user=*USERNAME* ansible_ssh_private_key_file=*KEYFILEPATH*
```

Execute ansible-playbook

    $ ansible-playbook deploy-jmeter-slave.yml -i inventories/host
    