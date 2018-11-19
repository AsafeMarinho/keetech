FROM nginx

MAINTAINER Raphael Rodrigues<raphael0608@gmail.com>

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y nginx nano openssl
RUN mkdir /etc/nginx/ssl

WORKDIR /etc/nginx/ssl/
ADD cert/server.key /etc/nginx/ssl/
ADD cert/server.crt /etc/nginx/ssl/

WORKDIR /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
ADD conf/nginx.conf /etc/nginx/
ADD conf/default.conf /etc/nginx/conf.d/

WORKDIR /etc/nginx/
