### MYHOUSE ###

### define base image
ARG SDK_VERSION
ARG ARCHITECTURE
FROM myhouseproject/myhouse-sdk-raspbian:${ARCHITECTURE}-${SDK_VERSION}

### install module's dependencies
RUN pip install RPi.GPIO

### copy files into the image
COPY . $WORKDIR
