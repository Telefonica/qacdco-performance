#!/usr/bin/sh
while getopts u:x:a:s:e:t:q:i:g: flag
do
    case "${flag}" in
        u) prometheus_base_url=${OPTARG};;
        x) user_pass=${OPTARG};;
        a) auth=${OPTARG};;
        s) start=${OPTARG};;
        e) end=${OPTARG};;
        t) step=${OPTARG};;
        q) queries=${OPTARG};;
        i) graphs_info=${OPTARG};;
        g) generate_graphs=${OPTARG};;
        *)
    esac
done

sudo docker build -f ./docker/Dockerfile . -t prometheus_chart_exporter:0.0.1

# Run with parameters
sudo rm -f /tmp/prometheus_exporter.cid
sudo docker run --cidfile /tmp/prometheus_exporter.cid -e prometheus_base_url="${prometheus_base_url}" \
       -e auth="${auth:-"None"}" -e user_pass="${user_pass:-"None"}" -e start="${start}" -e end="${end}" -e step="${step}" \
       -e queries="${queries}" -e graphs_info="${graphs_info}" -e generate_graphs="${generate_graphs:-"False"}" prometheus_chart_exporter:0.0.1
cid=$(sudo cat /tmp/prometheus_exporter.cid)
sudo docker cp "$cid":/script/output.json ./metrics.json
sudo docker cp "$cid":/script/output.html ./metrics.html
sudo docker rm "$cid"