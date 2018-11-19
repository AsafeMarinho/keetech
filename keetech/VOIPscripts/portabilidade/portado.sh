#!/bin/bash
user='root'
senha='PASSWORD'

mysql  -p"$senha"  -e "drop database portado;";
mysql  -p"$senha"  -e "drop database gsm;";
mysql  -p"$senha"  -e "create database portado;";
mysql  -p"$senha"  -e "create database gsm;";
mysql  -p"$senha"  -e "use portado;";

mysql  -p"$senha"  -e  " use gsm;
CREATE TABLE IF NOT EXISTS celular (
  id int(11) NOT NULL AUTO_INCREMENT,
  ddd int(6) NOT NULL,
  operadora int(1) NOT NULL,
  descr varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  obs varchar(255) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=297004 ;

"

mysql  -p"$senha"  -e  "use portado;
CREATE TABLE IF NOT EXISTS
telefone (
  numero bigint(20) NOT NULL,
  operadora int(11) NOT NULL,
  data date NOT NULL,
  PRIMARY KEY (numero)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

"
#mysqldump -u root -h189.6.77.50 -p'' --no-create-info --skip-add-drop-table -x -e -B portado  > resultado.sql
#mysql -u root -p"$senha" < resultado.sql
#rm resultado.sql

#mysqldump -u root -h189.6.77.50 -p'' --no-create-info --skip-add-drop-table -x -e -B portado  > resultado.sql
#mysql -u root -p"$senha" < resultado.sql
#rm resultado.sql
