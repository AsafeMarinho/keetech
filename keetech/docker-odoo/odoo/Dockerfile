# DOCKERFILE ODOO - DELTA OPEN SOLUTIONS CUSTOM

FROM ubuntu:trusty
MAINTAINER Rodrigues, Raphael <raphael0608@gmail.com>

#vriaveis para ambiente odoo
ENV ODOO_VERSION 11.0
ENV APP_VERSION 1
ENV APP_RELEASE 1.0
ENV PG_HOST db
ENV PG_PORT 5432
ENV PG_USER odoo
ENV PG_PASSWORD odoo
ENV PORT 8069

ENV DEBIAN_FRONTEND noninteractive

#instalando pacotes e configurando ambiente
RUN locale-gen pt_BR.UTF-8 \
    && update-locale LANG=pt_BR.UTF-8 \
    && ln -sf /usr/share/zoneinfo/America/Manaus /etc/localtime \
    && echo "America/Manaus" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# Install requirements for website build themes
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:ecometrica/servers
RUN apt-get update
RUN apt-get install -y npm

RUN npm config set strict-ssl false
RUN npm install -g less && npm cache clean
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN apt-get install -y gcc
RUN npm install -g less less-plugin-clean-css

# Install requirements & libs
WORKDIR /tmp/

ADD files/apt-requirements /tmp/apt-requirements
ADD files/pip-requirements /tmp/pip-requirements
RUN apt-get install -y --no-install-recommends $(grep -v '^#' apt-requirements)

# Instalando Wkhtmltox
ADD https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb /tmp/wkhtmltox-0.12.1_linux-trusty-amd64.deb
RUN dpkg -i /tmp/wkhtmltox-0.12.1_linux-trusty-amd64.deb
#Download do Wkhtmltopdf pelo link esta apresentando erros

RUN pip3 install --upgrade --force-reinstall pip==9.0.3
RUN pip3 install requests==2.11.1 --disable-pip-version-check
RUN pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools
RUN pip3 install --ignore-installed -r /tmp/pip-requirements

# Instalando PythonCnab, PythonBoleto e PyTrustNFe customizados
RUN mkdir /sources

# Estruturando o ambiente
WORKDIR /opt/

RUN bash -c \
    'mkdir -p /var/log/odoo'

RUN touch /var/log/odoo/odoo.log \
    && touch /var/run/odoo.pid

RUN git config --global http.postBuffer 2M
RUN git clone https://github.com/odoo/odoo --depth=1 -b 11.0

WORKDIR /opt/odoo/
ADD files/delta-config delta-config
RUN git config --global http.postBuffer 2M
RUN git clone https://github.com/Trust-Code/odoo-brasil -b 11.0 && \
    git clone https://github.com/OCA/server-tools -b 11.0 && \
    git clone https://github.com/OCA/project -b 11.0 && \
    git clone https://github.com/OCA/contract -b 11.0 && \
    git clone https://github.com/OCA/web -b 11.0 && \
    git clone https://github.com/Openworx/backend_theme -b 11.0 && \
    git clone https://github.com/Trust-Code/trustcode-addons -b 11.0

WORKDIR /opt/odoo/

# Limpando o ambiente
RUN apt-get autoremove -y && \
    apt-get autoclean

# Supervisor
ADD files/supervisord.conf /etc/supervisor/supervisord.conf

# Start
VOLUME ["/opt/odoo"]
CMD ["/usr/bin/supervisord"]
