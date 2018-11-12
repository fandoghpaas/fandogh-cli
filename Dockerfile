FROM alpine
RUN \
   apk --update add python3 py3-pip py3-openssl py3-cryptography py3-requests tzdata && \
   pip3 install --upgrade pip && \
   pip3 install fandogh-cli && \
   cp /usr/share/zoneinfo/Asia/Tehran /etc/localtime && \
   echo "Asia/Tehran" > /etc/timezone
