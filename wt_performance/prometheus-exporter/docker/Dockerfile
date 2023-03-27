FROM amancevice/pandas:1.5.1-alpine

RUN apk add --no-cache bash
COPY ./script/ /script/
COPY ./exporter.sh /exporter.sh
COPY docker/requirements.txt /
WORKDIR /script

RUN pip3 install -r /requirements.txt

ENTRYPOINT ["/bin/bash", "/exporter.sh"]