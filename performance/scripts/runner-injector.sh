DATA="user_count=${USER_COUNT}&spawn_rate=${SPAWN_RATE}&host=${TARGET_HOST}"
echo "Performance Tests execution"

echo -e "\n+++ Starting sysstat daemons for the injector"
ssh ubuntu@${HOST_INJECTOR} <<ENDSSH
sudo sed -i 's/ENABLED="false"/ENABLED="true"/g' /etc/default/sysstat
sudo service sysstat restart
ENDSSH
echo -e "\n+++ Started sysstat daemons for the injector"

START_TIME=$(date -u --date='3 minutes ago' | awk '{print $4}' |  awk '$0=substr($0,1,6)"00"')
echo "Start time to recollect host resources metrics: ${START_TIME}"

ssh ubuntu@${HOST_INJECTOR} "curl --data \"${DATA}\" http://localhost:8089/swarm --trace-ascii /dev/stdout"
sleep ${DURATION}
ssh ubuntu@${HOST_INJECTOR} "curl http://localhost:8089/stop"
END_TIME=$(date -u --date='3 minutes' | awk '{print $4}' |  awk '$0=substr($0,1,6)"00"')
END_TIME_INJECTOR=$(date -u | awk '{print $4}' |  awk '$0=substr($0,1,6)"00"')
echo "End time to recollect host resources metrics: ${END_TIME}"

echo -e "\n+++ Stopping sysstat daemons for the injector"
ssh ubuntu@${HOST_INJECTOR} <<ENDSSH
sudo sed -i 's/ENABLED="true"/ENABLED="false"/g' /etc/default/sysstat
sudo service sysstat restart
ENDSSH
echo -e "\n+++ Stopped sysstat daemons for the injector"

ssh ${PERFORMANCE_INJECTOR_USER}@${PERFORMANCE_INJECTOR_HOST} <<ENDSSH
mkdir -p /tmp/qacdo/performance/machine_measures_retrieval
cd /opt/qacdo/performance/machine_measures_retrieval/
sudo python MachineMeasuresRetrieval.py -i False -s ${START_TIME} -e ${END_TIME_INJECTOR} -path /tmp/qacdo/performance/machine_measures_retrieval
ENDSSH
sleep 2