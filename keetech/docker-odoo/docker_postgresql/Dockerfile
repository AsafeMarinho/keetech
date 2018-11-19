FROM ubuntu:trusty
MAINTAINER Rodrigues, Raphael <raphael0608@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

#Instalando o Postgresql
RUN apt-get update && \
    apt-get install -y postgresql-9.3 pwgen && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#Ajustando a configuração do PostgreSQL para que as conexões remotas com o banco de dados sejam possíveis.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf


#Adicionar VOLUMEs para permitir backup de config, logs e bancos de dados
VOLUME	["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

ADD modify_postgres_pass.sh ./modify_postgres_pass.sh
ADD run.sh /run.sh
RUN chmod 755 /*.sh

EXPOSE 5432
CMD ["/run.sh"]
