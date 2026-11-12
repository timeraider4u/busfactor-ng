FROM docker.io/library/python:2.7-slim

ARG GH_HOST=github.com
ARG GH_ORG=SOM-Research

RUN sed -i 's|deb.debian.org/debian|archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list && \
    apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -y --no-install-recommends \
    git \
    default-mysql-client \
    python-tk \
    python-pyqt5 \
    python-numpy \
    python-psutil \
    python-lxml \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone "https://${GH_HOST}/${GH_ORG}/Gitana.git" /opt/Gitana && \
    git clone "https://${GH_HOST}/${GH_ORG}/busfactor.git" /opt/busfactor

RUN pip install --no-cache-dir \
    networkx==2.2 \
    mysql-connector-python==8.0.23 \
    gitpython==2.1.15 \
    beautifulsoup4==4.9.3 \
    BeautifulSoup==3.2.2 \
    pygithub==1.45 \
    pygal==2.4.0 \
    slacker==0.14.0 \
    python-bugzilla==2.5.0 \
    requests==2.27.1 \
    python-dateutil==2.8.2 \
    psutil==5.9.8 \
    numpy==1.16.6

RUN cd /opt/Gitana && pip install --no-deps .

RUN chmod -R 777 /app /opt/busfactor

COPY gitana_extract.py /app/gitana_extract.py
