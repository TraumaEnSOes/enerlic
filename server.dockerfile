FROM python:3.10.11-slim
COPY src/ /opt/enerlic_0.1
EXPOSE 4444
RUN apt-get update; apt-get install -y dumb-init; apt-get clean
ENTRYPOINT [ "/usr/bin/dumb-init", "/usr/local/bin/python", "/opt/enerlic_0.1/server.py" ]
