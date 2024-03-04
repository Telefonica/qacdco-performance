# Locust performance testing framework

This Performance Testing Framework uses Locust, an opensource tool based on Python, with which we can easily create our own performance scenarios. You can access the Documentation and Locust Source Code [here](https://locust.io/). Below is a summarized guide of the Framework, a step-by-step guide to set it up can be found in [Confluence](https://confluence.tid.es/pages/viewpage.action?pageId=73025608).

## Structure
````
Performance Project
│
└─── Apis
│   │   apis.py In this file the different requests of the applications are defined, usually one class 
│   │   is defined per api
│   
└─── CI
│   │   jenkinsfile: This file contains the generic structurae as an example of the jenkinsfile that  │   │   That we can use to set up pthe performance pipeline in our project.
│
│
└─── Injectors
│    │  Dockerfile: This file contains the Locust docker image that will be deployed 
│    │              on the master and workers machines
│
└─── Scenarios
│    │ 
│    └─── Common
│    │    │
│    │    │     hooks.py: Methods iumplemented for communicationb between masters and workers
│    │  
│    │   global.py: This file contains the performance scenarios to be executed
│
└─── scripts
│   │   upload_to_reporter.sh: Script that will upload the test results to the Performance Reporter
│   │   runner-locust.sh: Script that will execute the performance scenario (called by jenkins)
│ 
│ docker-compose.yaml: This file defines master and worker services.

````
## Using the Framework
If you are interested on trying the the Locust framework before you start implementing it in your project, you can go to the perf/example branch in this repository and use the example there, it's ready to be deployed and used.

## Example Framework

We have a simple example of locust framework on directory ```./locust_example```

# EXECUTION INSTRUCTIONS

1. Start the injector that will be used:
    * Go to the following jenkins job [Link](https://pro-dcip-qacdo-01.hi.inet/job/WT_INFRASTRUCTURE/job/WTI_DEVOPS_AWS_start_stop_instances), click on "Build with Parameters" on the left panel, select "***start***", the injector "***qacdo-en-pro-performance-inj01***" and execute the build.

    * Copy the public ip given to this injector in the console output of the build.

2. Job execution:
    * In the following jenkins job [link](https://pro-dcip-qacdo-01.hi.inet/job/WT_PERFORMANCE/job/locust_infra_test), click on "***Build with Parameters***" button in the left panel. Fill in the parameter "**HOST_INJECTOR**" with the ip of the injector to use. The rest of the parameters can be modified as needed, but with the default settings, the test is functional.

3. Review of metrics:
    * Although our Jenkins pipeline generates graphs of results. More information and metrics can be found in the [Performance Reporter](http://qacdco.hi.inet/pre-performance/reporter/projects), to see them, go to the Performance Reporter and access the execution performed within the LOCUST project for a better analysis.

# PERFORMANCE TEST
## Test Description

First you need to go to the example_locust directory:

```bash
cd ./locust_example

```

First you need to create a .env file with the following variables:

> [!IMPORTANT]
> Modify HOME_PATH variable to your working directory

```bash

SAMPLING=1
TEST=global.py
HOME_PATH=/home/davidg/git/telefonica/qacdco-performance/locust/locust_example


```
run the following command to start the test:


```bash
docker-compose --env-file .env -f docker-compose.yaml up -d --force-recreate

```

Use your browser to access the locust web interface at http://localhost:8089
