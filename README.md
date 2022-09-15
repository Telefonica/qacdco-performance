# EXECUTION INSTRUCTIONS
1. Start the injector that will be used:
    * Go to the following jenkins job [Link](https://pro-dcip-qacdo-01.hi.inet/job/WT_INFRASTRUCTURE/job/WTI_DEVOPS_AWS_start_stop_instances), click on "Build with Parameters" on the left panel, select "***start***", the injector "***qacdo-en-pro-performance-inj01***" and execute the build.

    * Copy the public ip given to this injector in the console output of the build.

2. Job execution:
    * In the following jenkins job [link](https://pro-dcip-qacdo-01.hi.inet/job/WT_PERFORMANCE/job/locust_infra_test), click on "***Build with Parameters***" button in the left panel. Fill in the parameter "**HOST_INJECTOR**" with the ip of the injector to use. The rest of the parameters can be modified as needed, but with the default settings, the test is functional.

3. Review of metrics:
    * Although our Jenkins pipeline generates graphs of results. More information and metrics can be found in the [Performance Reporter](http://qacdco.hi.inet/pre-performance/reporter/projects), to see them, go to the Performance Reporter and access the execution performed within the LOCUST project for a better analysis.