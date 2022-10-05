# Machine Metrics Retrieval Script
An important part of running performance tests is to make sure that the machines running the tests are not overloaded, for that the Performance Framework has a script that will install Prometheus (monitoring and alerting system) and node_exporter (prometheus module that takes the resource usage metrics), to export the Hardware and Operating System usage metrics to the Grafana of the project.
## Instalation
 Clone the performance repository on the injector machine 
 
 ``git clone https://github.com/Telefonica/qacdco-performance``

 navigate to the machine_measures_retrieval directory and run the install.sh script with root permissions.
 
 ``sudo ./install.sh`` 
 
 once the script has run navigate to your project's Grafana and create a new data source.
 make sure that the machine hosting the Grafana has access to the injector machine (If you are using the External IP make sure to open the port 9090, use the Local IP if they are on the same network, etc).
 Finally, create a new dashboard in the project, you can import the json performance.json or create your own.
