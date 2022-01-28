# Copyright (c) Telefonica Digital - CDO QA Team
# Inspired on  cirit/jmeter docker image: https://hub.docker.com/r/cirit/jmeter/

FROM jmeter:latest

# Port 24000 for the JMeter connection and port 26000 for RMI from client to server
EXPOSE 24000
EXPOSE 26000

ENTRYPOINT ["jmeter-server", "-Jserver.rmi.ssl.disable=true", "-Djava.rmi.server.hostname=127.0.0.1", "-Jserver_port=24000", "-Jserver.rmi.localhostname=127.0.0.1", "-Jserver.rmi.localport=26000"]

