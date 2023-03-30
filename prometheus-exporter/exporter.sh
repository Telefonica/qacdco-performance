#!/usr/bin/sh

#define parameters from env passing by docker run
queries="${queries}"
prometheus_base_url="${prometheus_base_url}"
auth="${auth}"
user_pass="${user_pass}"
start="${start}"
end="${end}"
step="${step}"
formatted_queries="${formatted_queries}"

formatted_queries=$(echo "${queries}" | awk -v FS=";" '{ for (i=1; i<=NF; i++) { printf "'\''%s'\''", $i; if (i!=NF) printf " "}}')
if [ "${user_pass}" != "None" ]; then
    python prometheus_chart_exporter.py -u "${prometheus_base_url}" -x "${user_pass}" -s "${start}" -e "${end}" -t "${step}" -q "${formatted_queries}"
elif [ "${auth}" != "None" ]; then
    python prometheus_chart_exporter.py -u "${prometheus_base_url}" -a "${auth}" -s "${start}" -e "${end}" -t "${step}" -q "${formatted_queries}"
else
    python prometheus_chart_exporter.py -u "${prometheus_base_url}" -s "${start}" -e "${end}" -t "${step}" -q "${formatted_queries}"
fi