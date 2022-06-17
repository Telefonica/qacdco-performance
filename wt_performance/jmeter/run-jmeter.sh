#!/usr/bin/env bash

# Copyright Telefonica Digital
# CDO QA Team <qacdo@telefonica.com>

# JMeter execution with UI using your local jmeter installation. To be used for development purposes.
# Is you use the option -d, a NON-UI JMeter execution mode is launch using a docker container

DOCKER_IMAGE=dockerhub.hi.inet/dcip/qa-cdo-perf

usage="$(basename "$0") [-h] [-t test-file] [-d] [-i] [-h host-address] [-u host-user] [-r]-- open JMeter in your workspace (development mode) or run it into docker container

where:
    -h  Show this help text
    -t  Name of the JMeter script to be executed (jmx script name located at 'jmeter/script' subdir without extension). Default: test_script
    -d  If set, the execution will be performed in NON-UI mode using docker a container
    -i  If set, use a remote injector. The following commands are necessary if we use this option
    -a  Host address of the remote injector. Needed with the -i option.
    -u  User of the remote injector. Default: Ubuntu, optional with the -i option.
    -r  If set, retrieve the host measures from the machines set in config folder. optional with the -i option."

PERFORMANCE_JMETER_SCRIPT_NAME="test_script"
PERFORMANCE_OBTAIN_HOST_MEASURES="No"
PERFORMANCE_INJECTOR_USER=ubuntu
while getopts 'hdt:ia:ur' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    d) docker=true
       ;;
    t) PERFORMANCE_JMETER_SCRIPT_NAME=$OPTARG
       ;;
    i) injector=true
       ;;
    a) PERFORMANCE_INJECTOR_HOST=$OPTARG
       ;;
    u) PERFORMANCE_INJECTOR_USER=$OPTARG
       ;;
    r) PERFORMANCE_OBTAIN_HOST_MEASURES="Yes"
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
    \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
  esac
done
shift $((OPTIND - 1))

echo "[CDO QA Team] Performance Tests execution"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

if [[ ${docker} == "true" ]] ; then
  echo "+++ DOCKER: Run JMeter in Docker [Docker image ${DOCKER_IMAGE}]"
  OUTPUT_FOLDER="./output/${PERFORMANCE_JMETER_SCRIPT_NAME}_${TIMESTAMP}"
  mkdir -p $OUTPUT_FOLDER
  docker run \
    -v `pwd`/:/qacdo-perf \
    -w /qacdo-perf \
    $DOCKER_IMAGE \
    jmeter -n -e -j $OUTPUT_FOLDER/jmeter.log -l $OUTPUT_FOLDER/samples.csv -t jmeter/${PERFORMANCE_JMETER_SCRIPT_NAME}.jmx -o $OUTPUT_FOLDER/html-report

elif [[ ${injector} == "true" ]] ; then
  echo "+++ DOCKER: Run JMeter in injector [Performance injector ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST}]"
  # Create directory for all output files
  TIMESTAMP=$(date +%Y%m%d%H%M%S)
  OUTPUT_FOLDER="./output/${SCRIPT_NAME}_${PERFORMANCE_INJECTOR_HOST}_${TIMESTAMP}"
  sudo docker-compose run -e PERFORMANCE_INJECTOR_HOST=$PERFORMANCE_INJECTOR_HOST -e PERFORMANCE_INJECTOR_USER=$PERFORMANCE_INJECTOR_USER -e PERFORMANCE_OBTAIN_HOST_MEASURES=$PERFORMANCE_OBTAIN_HOST_MEASURES -e PERFORMANCE_JMETER_SCRIPT_NAME=$PERFORMANCE_JMETER_SCRIPT_NAME -e TIMESTAMP=$TIMESTAMP -e OUTPUT_FOLDER=$OUTPUT_FOLDER perf bash -c "cd qacdoperf && sh run-jmeter-remote-slave.sh"

else
  echo "+++ LOCAL: Open JMeter UI for test file: 'jmeter/${PERFORMANCE_JMETER_SCRIPT_NAME}.jmx'"
  OUTPUT_FOLDER="./output/${PERFORMANCE_JMETER_SCRIPT_NAME}_${TIMESTAMP}"
  mkdir -p $OUTPUT_FOLDER
  jmeter -t jmeter/${PERFORMANCE_JMETER_SCRIPT_NAME}.jmx

fi
