#qa-cdo-perf Docker image
Dockerfile image for the Working Team Performance.

##Artifactory update
After any changes done to it, it has to be updated in the dcip artifactory.
For that use this job: https://pro-dcip-qacdo-01.hi.inet/job/WT_JENKINS/job/_docker-slave-builder-qa-cdo-perf_dcip2/

##Local 

Build the image with: 
```
docker build -f dcip-qa-cdo-perf/Dockerfile .
```
It's really important to execute this command while being in `qacdco-tools/performance_framework` so the build context is 
correct.