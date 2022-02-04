#!/usr/bin/env bash

# Copyright Telefonica Digital
# CDO QA Team <qacdo@telefonica.com>


# NON-UI JMeter execution mode using remote node injector (JMeter slave node)
if [ "$QA_REPORTER_ENVIRONMENT" == "PRO" ]; then
  QA_REPORTER_URL="https://qacdco.d-consumer.com/qareporter"
elif [ "$QA_REPORTER_ENVIRONMENT" == "PRE" ]; then
  QA_REPORTER_URL="http://qacdco.hi.inet/qaperformance-pre"
else
  echo "Error, QA_REPORTER_URL must be PRE or PRO. Exiting..."
  exit -1
fi

echo -e "\n\n+++ Upload data to QA Reporter"

PROJECT_OBJECT=$(curl -X GET "${QA_REPORTER_URL}/api/1.0/performance/projects/?name=${PERFORMANCE_PROJECT_NAME}")
PROJECT_OBJECT=${PROJECT_OBJECT##[}
PROJECT_OBJECT=${PROJECT_OBJECT%]}

if (( ${#PROJECT_OBJECT} )); then
  PROJECT_ID=$(echo "${PROJECT_OBJECT}" | awk -v FS="(project_id\":|,)" '{print $2}')
  EXECUTION_DATE=$(date +"%Y-%m-%d %H:%M")

  EXECUTION_OBJECT=$(curl -X POST -d "name=autoexecution_${PERFORMANCE_VERSION_NUMBER}&project-id=${PROJECT_ID}&module=${PERFORMANCE_PROJECT_MODULE}&version=${PERFORMANCE_VERSION_NUMBER}&date=${EXECUTION_DATE}" ${QA_REPORTER_URL}/api/1.0/performance/executions/)
  EXECUTION_ID=$(echo "${EXECUTION_OBJECT}" | awk -v FS="(execution_id\": |})" '{print $2}' | awk -F "," '{print $1}')


  cd ${PERFORMANCE_PROJECT_PATH}/${OUTPUT_FOLDER}
  curl -X POST -F "module=${PERFORMANCE_PROJECT_MODULE}" -F "data=@jmeter/samples.csv" -F "project-id=${PROJECT_ID}" -F "execution-id=${EXECUTION_ID}" -F 'input-type=jmeter-csv' ${QA_REPORTER_URL}/api/1.0/performance/csv_loader

  if [ "${PERFORMANCE_OBTAIN_HOST_MEASURES}" = "Yes" ]; then

      for file_cpu in "hosts/tmp_collectd_cpu_"*
      do
        curl -X POST -F "module=${PERFORMANCE_PROJECT_MODULE}" -F "data=@$file_cpu" -F "project-id=${PROJECT_ID}" -F "execution-id=${EXECUTION_ID}" -F 'input-type=cpu-csv' ${QA_REPORTER_URL}/api/1.0/performance/csv_loader
      done

      for file_disk in "hosts/tmp_collectd_disk_"*
      do
        curl -X POST -F "module=${PERFORMANCE_PROJECT_MODULE}" -F "data=@$file_disk" -F "project-id=${PROJECT_ID}" -F "execution-id=${EXECUTION_ID}" -F 'input-type=disk-csv' ${QA_REPORTER_URL}/api/1.0/performance/csv_loader
      done

      for file_mem in "hosts/tmp_collectd_memory_"*
      do
        curl -X POST -F "module=${PERFORMANCE_PROJECT_MODULE}" -F "data=@$file_mem" -F "project-id=${PROJECT_ID}" -F "execution-id=${EXECUTION_ID}" -F 'input-type=memory-csv' ${QA_REPORTER_URL}/api/1.0/performance/csv_loader
      done

      for file_net in "hosts/tmp_collectd_network_"*
      do
        curl -X POST -F "module=${PERFORMANCE_PROJECT_MODULE}" -F "data=@$file_net" -F "project-id=${PROJECT_ID}" -F "execution-id=${EXECUTION_ID}" -F 'input-type=network-csv' ${QA_REPORTER_URL}/api/1.0/performance/csv_loader
      done

  else
    echo "No host measures metrics to upload"
  fi

else
  echo "Project not found"
  echo "Upload to QA Reported aborted"
  exit -1
fi
