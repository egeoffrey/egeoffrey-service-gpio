### EGEOFFREY ###

### define base image
ARG SDK_VERSION
ARG ARCHITECTURE
FROM egeoffrey/egeoffrey-sdk-raspbian:${SDK_VERSION}-${ARCHITECTURE}

### install module's dependencies
RUN pip install RPi.GPIO

### copy files into the image
COPY . $WORKDIR
