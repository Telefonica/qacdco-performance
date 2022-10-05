#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

sudo useradd -rs /bin/false node_exporter

useradd --no-create-home --shell /bin/false prometheus
mkdir /etc/prometheus
mkdir /var/lib/prometheus
chown prometheus:prometheus /etc/prometheus
chown prometheus:prometheus /var/lib/prometheus

wget https://github.com/prometheus/prometheus/releases/download/v2.38.0/prometheus-2.38.0.linux-amd64.tar.gz -O "/tmp/prometheus.tar.gz"
tar -xf "/tmp/prometheus.tar.gz" -C "/tmp"
mv "/tmp/prometheus-2.38.0.linux-amd64" "/tmp/prometheus-files"
cp /tmp/prometheus-files/prometheus /usr/local/bin/
cp /tmp/prometheus-files/promtool /usr/local/bin/
chown prometheus:prometheus /usr/local/bin/prometheus
chown prometheus:prometheus /usr/local/bin/promtool
cp -r /tmp/prometheus-files/consoles /etc/prometheus
cp -r /tmp/prometheus-files/console_libraries /etc/prometheus
cp prometheus.yml /etc/prometheus/prometheus.yml
chown prometheus:prometheus /etc/prometheus/prometheus.yml

wget https://github.com/prometheus/node_exporter/releases/download/v1.4.0-rc.0/node_exporter-1.4.0-rc.0.linux-amd64.tar.gz -O "/tmp/node_exporter.tar.gz"
tar -xf "/tmp/node_exporter.tar.gz" -C "/tmp"
mv "/tmp/node_exporter-1.4.0-rc.0.linux-amd64" "/tmp/node_exporter"
mv "/tmp/node_exporter-1.4.0-rc.0.linux-amd64/node_exporter" "/usr/local/bin/"

echo "[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/prometheus.service

echo "[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/node_exporter.service