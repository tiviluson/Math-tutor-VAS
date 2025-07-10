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
RUN pip install --no-cache-dir google-generativeai
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

WORKDIR /app

COPY olympiad.asy /root/.asymptote/
COPY run.asy /root/.asymptote/ 
COPY viz_tool.py /app/
COPY viz_prompts.py /app/


ENV ASYMPTOTE_TEXPATH="/usr/bin"
ENV ASYMPTOTE_MAGICKPATH="/usr/bin"

CMD ["tail", "-f", "/dev/null"]