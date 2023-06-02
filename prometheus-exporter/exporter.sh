#!/usr/bin/sh

#define parameters from env passing by docker run
queries="${queries}"
prometheus_base_url="${prometheus_base_url}"
auth="${auth}"
user_pass="${user_pass}"
start="${start}"
end="${end}"
step="${step}"
queries_file="${queries_file}"
generate_graphs="${generate_graphs}"

if [ "${user_pass}" != "None" ]; then
    python prometheus_chart_exporter.py -u "${prometheus_base_url}" -x "${user_pass}" -s "${start}" -e "${end}" -t "${step}" -f "${queries_file}" -g "${generate_graphs}"
elif [ "${auth}" != "None" ]; then
    python prometheus_chart_exporter.py -u "${prometheus_base_url}" -a "${auth}" -s "${start}" -e "${end}" -t "${step}" -f "${queries_file}" -g "${generate_graphs}"
else
    python prometheus_chart_exporter.py -u "${prometheus_base_url}" -s "${start}" -e "${end}" -t "${step}" -f "${queries_file}" -g "${generate_graphs}"
fi