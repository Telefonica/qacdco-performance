# Copyright (c) Telefonica Digital - CDO QA Team

FROM dockerhub.hi.inet/dcip/qa-cdo:latest

ARG JMETER_VERSION="4.0"
ENV JMETER_HOME /opt/apache-jmeter-${JMETER_VERSION}
ENV	JMETER_BIN	${JMETER_HOME}/bin
ENV	JMETER_DOWNLOAD_URL  https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz

# Download jMeter
RUN curl -L --silent ${JMETER_DOWNLOAD_URL} >  /tmp/apache-jmeter-${JMETER_VERSION}.tgz
RUN tar -xzf /tmp/apache-jmeter-${JMETER_VERSION}.tgz -C /opt
RUN chown -R contint:contint /opt/apache-jmeter-${JMETER_VERSION}
RUN rm -rf /tmp/apache-jmeter-${JMETER_VERSION}.tgz
RUN ln -s /opt/apache-jmeter-${JMETER_VERSION}/bin/jmeter /usr/bin/jmeter

# Add influxdb and Grafana scripts
ADD csv_to_influxdb /opt/csv_to_influxdb
RUN pip install -r /opt/csv_to_influxdb/requirements.txt

# Switch to root user (required by dcip)
USER root
