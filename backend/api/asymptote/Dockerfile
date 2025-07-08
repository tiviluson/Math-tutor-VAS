FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    asymptote \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-pictures \
    imagemagick \
    dvisvgm \
    ghostscript && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

RUN mkdir -p /root/.asymptote/
COPY olympiad.asy /root/.asymptote/

COPY run.asy /root/.asymptote/

ENV ASYMPTOTE_TEXPATH="/usr/bin"
ENV ASYMPTOTE_MAGICKPATH="/usr/bin"

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]