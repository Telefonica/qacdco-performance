#!/bin/bash
PROJECT_OBJECT=$(curl -x "" -X GET http://qacdco.hi.inet/pre-performance/reporter/api/1.0/projects/?name=${PERFORMANCE_PROJECT_NAME})
PROJECT_OBJECT=${PROJECT_OBJECT##[}
PROJECT_OBJECT=${PROJECT_OBJECT%]}
PROJECT_ID=$(echo ${PROJECT_OBJECT} | awk -v FS="(project_id\":|,)" '{print $2}')
EXECUTION_DATE=$(date +"%Y-%m-%d %H:%M")
EXECUTION_OBJECT=$(curl -X POST -F "project-id=${PROJECT_ID}" -F "module=${SCENARIO}" -F "name=${PERFORMANCE_EXECUTION_NAME}" -F "type=LOAD" -F "version=${RELEASE_VERSION}" -F "date=${EXECUTION_DATE}" http://qacdco.hi.inet/pre-performance/reporter/api/1.0/executions/)
EXECUTION_ID=$(echo "${EXECUTION_OBJECT}" | awk -v FS="(execution_id\": |})" '{print $2}' | awk -F "," '{print $1}')
curl -X POST -F data=@locust_results.csv -F execution-id=${EXECUTION_ID} -F input-type=jmeter-csv ${QA_REPORTER_URL}/api/1.0/csv_loader
