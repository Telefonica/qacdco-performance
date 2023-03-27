#!/usr/bin/sh

#define parameters from env passing by docker run
queries="${queries}"
prometheus_base_url="${prometheus_base_url}"
auth="${auth}"
start="${start}"
end="${end}"
step="${step}"
formatted_queries="${formatted_queries}"

formatted_queries=$(echo "${queries}" | awk -v FS=";" '{ for (i=1; i<=NF; i++) { printf "'\''%s'\''", $i; if (i!=NF) printf " "}}')
python prometheus_chart_exporter.py -u "${prometheus_base_url}" -a "${auth}" -s "${start}" -e "${end}" -t "${step}" -q "${formatted_queries}"
