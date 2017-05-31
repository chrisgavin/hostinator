FROM alpine:3.6

RUN apk add --no-cache --update python3
RUN python3 -m ensurepip

ADD "." "/tmp/hostinator/"
RUN pip3 install "/tmp/hostinator/"

VOLUME "/var/run/docker.sock"
VOLUME "/mnt/etc/"
ENV "HOSTS_DIR" "/mnt/etc/"
ENTRYPOINT ["hostinator"]
