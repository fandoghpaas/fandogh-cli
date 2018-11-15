FROM alpine
RUN apk --update add python3 py3-pip py3-openssl py3-cryptography py3-requests tzdata && \
    pip3 install --upgrade pip && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone
RUN mkdir -p /fandogh
WORKDIR /fandogh
COPY requirements.txt /fandogh
RUN pip install -r /fandogh/requirements.txt
COPY fandogh_cli /fandogh/fandogh_cli
RUN echo -e '#!/usr/bin/python3 \nimport sys \nfrom fandogh_cli.fandogh import base \nsys.exit(base())'> /usr/bin/fandogh && \
    chmod +x /usr/bin/fandogh
ENV PYTHONPATH "${PYTONPATH}:/fandogh/"
CMD ["fandogh"]
