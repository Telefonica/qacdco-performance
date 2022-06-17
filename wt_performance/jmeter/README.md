Test execution tools
====================

The script that we are going to use to launch all the process from local is run-jmeter.sh

This script has as objective:
* Execute the performance tests in local using the jmeter instance that the user has installed
* Execute the performance tests in local using a docker image supported by the working team (qa-cdo-perf)
* Execute the performance tests in a remote inyector

Prerequisites
---
# Local execution using only JMeter
Have an instance of JMeter installed and in the environment path and be located in the TID network.

# Local execution using Docker 
Have Docker installed in your computer.

This script DOES NOT work with Windows, in that case a Virtual Machine would be needed. 

Have the CA certificate of TID be installed in our system. This is needed to pull the docker image of the working team. 

# Remote execution in the injector
Same steps as using the Docker image and your ssh key should be authorized by the injector.

Use
---

bash ./run-jmeter.sh

# Local
No need of an additional flag. With -t we can change the test name that we have stored. Default is test_script.

# Docker
Invoked with the -d flag.

# Remote execution with the injector
Flag -i would invoke the remote injector. Alongside this, we have to also add -a <INJECTOR_ADDRESS> in order to connect
to a machine. 

Using the flag -r, the injector would return the host measure resource metrics from the machines specified in the 
config folder. By default, they would not be returned so you don't need to setup the machines configuration.

The default user to connect to the injector is Ubuntu, with -u <INJECTOR_USER> the user can change it.

!!!!!!!!!!!!!!IMPORTANT!!!!!!!!!!!!!!

-d and -i options are exclusive, if you use both the script will be only executed in local using docker.

Examples
--------------

# Local execution with Docker

bash ./run-jmeter.sh -d

# Remote execution in an injector to obtain both the results of the performance tests and the host machine measures.

bash ./run-jmeter.sh -i -a 34.250.223.118 -r -u ubuntu -t test_script_api

