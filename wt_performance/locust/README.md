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
