FROM amancevice/pandas:1.5.1-alpine

RUN apk add --no-cache bash
COPY ./script/ /script/
COPY docker/requirements.txt /
WORKDIR /script
RUN pip3 install -r /requirements.txt

ENTRYPOINT ["python", "prometheus_chart_exporter.py"]
CMD ["default/path/to/config.yaml"]
