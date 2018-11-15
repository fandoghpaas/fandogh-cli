FROM alpine
RUN \
   apk --update add python3 py3-pip py3-openssl py3-cryptography py3-requests tzdata && \
   pip3 install --upgrade pip && \
   cp /usr/share/zoneinfo/Asia/Tehran /etc/localtime && \
   echo "Asia/Tehran" > /etc/timezone

ENV COLLECT_ERROR True
WORKDIR /opt/fandogh_cli
COPY . /opt/fandogh_cli
RUN pip3 install -r requirements.txt
RUN python3 setup.py install
