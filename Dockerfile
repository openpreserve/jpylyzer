FROM python:3.6-alpine as builder

LABEL maintainer="carl.wilson@openpreservation.org" \
      org.openpreservation.vendor="Open Preservation Foundation" \
      version="0.1"

RUN  apk update && apk --no-cache --update-cache add gcc build-base git libxml2-dev libxslt-dev

WORKDIR /src
RUN git clone https://github.com/openpreserve/jpylyzer.git
RUN mkdir /install && cd /src/jpylyzer && pip install -U pip && pip install --install-option="--prefix=/install" .

FROM python:3.6-alpine

RUN apk update && apk add --no-cache --update-cache libc6-compat libstdc++ bash

COPY --from=builder /install /usr/local

ENTRYPOINT ["jpylyzer"]
CMD ["-h"]
