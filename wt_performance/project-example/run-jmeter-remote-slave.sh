#!/usr/bin/env bash

# Copyright Telefonica Digital
# CDO QA Team <qacdo@telefonica.com>

# NON-UI JMeter execution mode using remote node injector (JMeter slave node)

# This script has been developed to be executed by Jenkins (DCIP) in order to use remote injectors for performing.
# test executions. The configuration of the execution will be managed by environment variables.
# This job is configured to run script following the project structure defined by WT-Performance for QA CDO Team.
# Required environments variables:
#          PERFORMANCE_PROJECT_PATH: Local relative path in the repository where performance project is located.
#          PERFORMANCE_JMETER_SCRIPT_NAME: Name of the jmeter script to be executed (name of the script located in jmeter folder without extension).
#          PERFORMANCE_OUTPUT_FORMAT: Format of the result files: csv or xml (defaul: csv)
#
#          PERFORMANCE_INJECTOR_HOST: Hostname of the injector node (JMeter slave).
#                                     contint public ssh key should be authorized to make ssh connections to that host.
#                                     JMeter slave node is running with the properly configuration in that nodes.

echo "[CDO QA Team] Performance Tests execution"

# Used to separate executions
FOLDER_ID=$(uuidgen | cut -c1-8)

# Move into performance tests project following the structure defined by WT-Performance.
cd ${PERFORMANCE_PROJECT_PATH:-./}

echo -e "\n+++ Sending recource files if needed to JMeter Slave node ${PERFORMANCE_INJECTOR_HOST}"
files=(jmeter/resources/*)

if [ ${#files[@]} -gt 0 ]; then scp ${files[@]} ubuntu@$PERFORMANCE_INJECTOR_HOST:/opt/qacdo/performance/shared_folder; fi

echo -e "\n+++ Starting ssh tunnels with injector nodes (JMeter Slave node): ${PERFORMANCE_INJECTOR_HOST}"
ssh -L 24000:127.0.0.1:24000 -L 26000:127.0.0.1:26000 -R 25000:127.0.0.1:25000 ubuntu@$PERFORMANCE_INJECTOR_HOST -fN -M -S injector-tunnel

echo -e "\n+++ Checking tunnel status with JMeter Slave node ${PERFORMANCE_INJECTOR_HOST}"
ssh -S injector-tunnel -O check ubuntu@$PERFORMANCE_INJECTOR_HOST

SCRIPT_NAME=${PERFORMANCE_JMETER_SCRIPT_NAME:-test_script}
REMOTE_INJECTOR_CONFIG="-R nt-jmeter-slave-1.westeurope.cloudapp.azure.com:25000,nt-jmeter-slave-2.westeurope.cloudapp.azure.com:25000 -Jserver.rmi.ssl.disable=true -Djava.rmi.server.hostname=127.0.0.1 -Jclient.rmi.localport=25000 -Jmode=Batch"
OUTPUT_FORMAT="-Jjmeter.save.saveservice.output_format=${PERFORMANCE_OUTPUT_FORMAT:-csv}"
if [ "$PERFORMANCE_OUTPUT_FORMAT" = "csv" ]; then
   GENERATE_REPORT_OPTION="-e"
fi

mkdir -p ${OUTPUT_FOLDER}

echo -e "\n+++ Starting sysstat daemons for the injector"
ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} <<ENDSSH
sudo sed -i 's/ENABLED="false"/ENABLED="true"/g' /etc/default/sysstat
sudo service sysstat restart
ENDSSH
echo -e "\n+++ Started sysstat daemons for the injector"

echo -e "\n+++ Running JMeter without UI for test file 'jmeter/${SCRIPT_NAME}.jmx' using remote injector node"

START_TIME=$(date -u --date='3 minutes ago' | awk '{print $4}' |  awk '$0=substr($0,1,6)"00"')

echo "Start time to recollect host resources metrics: ${START_TIME}"
jmeter -n -j ${OUTPUT_FOLDER}/jmeter/jmeter.log -l ${OUTPUT_FOLDER}/jmeter/samples.${PERFORMANCE_OUTPUT_FORMAT:-csv} -t jmeter/${SCRIPT_NAME}.jmx -o ${OUTPUT_FOLDER}/jmeter/html-report ${REMOTE_INJECTOR_CONFIG} ${OUTPUT_FORMAT} ${GENERATE_REPORT_OPTION}

echo -e "\n+++ Stopping ssh tunnels with injector nodes (JMeter Slave node): ${PERFORMANCE_INJECTOR_HOST}"
ssh -S injector-tunnel -O exit ubuntu@$PERFORMANCE_INJECTOR_HOST

END_TIME=$(date -u --date='3 minutes' | awk '{print $4}' |  awk '$0=substr($0,1,6)"00"')
END_TIME_INJECTOR=$(date -u | awk '{print $4}' |  awk '$0=substr($0,1,6)"00"')
echo "End time to recollect host resources metrics: ${END_TIME}"

ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} "
    mkdir -p /tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}/machine_measures" &&
    scp -r config/properties.ini ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST}:/tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}

ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} <<ENDSSH
cd /opt/qacdo/performance/machine_measures_retrieval/
sudo python MachineMeasuresRetrieval.py -i False -s ${START_TIME} -e ${END_TIME_INJECTOR} -path /tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}
ENDSSH

echo -e "\n+++ Stopping sysstat daemons for the injector"
ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} <<ENDSSH
sudo sed -i 's/ENABLED="true"/ENABLED="false"/g' /etc/default/sysstat
sudo service sysstat restart
ENDSSH

echo -e "\n+++ Stopped sysstat daemons for the injector"

if [ "${PERFORMANCE_OBTAIN_HOST_MEASURES}" = "Yes" ]; then
echo -e "\n+++ Wait 3 minutes for the sysstat to collect final metrics"
sleep 3m

ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} <<ENDSSH
cd /opt/qacdo/performance/machine_measures_retrieval/
sudo python MachineMeasuresRetrieval.py -s ${START_TIME} -e ${END_TIME} -path /tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}
ENDSSH
fi

mkdir -p ${OUTPUT_FOLDER}/hosts
scp -r ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST}:/tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}/machine_measures/* ${OUTPUT_FOLDER}/hosts
scp ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST}:/tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}/machine_measures.log ${OUTPUT_FOLDER}/hosts

ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} "sudo rm -r /tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}"
