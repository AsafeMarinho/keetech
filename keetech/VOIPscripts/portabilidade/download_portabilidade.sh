#!/bin/bash

user='root'
senha='PASSWORD'
accesso='TEST:PASSWORD'
#servidor='191.34.33.67'
servidor='186.249.1.158:62221'

cd /var/srv/

rm /var/srv/hash.txt
rm /var/srv/telefone.tar
rm /tmp/telefone.csv
wget http://"$accesso"@"$servidor"/hash.txt
wget http://"$accesso"@"$servidor"/telefone.tar
tar -zxvf telefone.tar
mv  /var/srv/telefone.csv /tmp/telefone.csv

original=$(cat /var/srv/hash.txt)

atual=$(cat /tmp/telefone.csv | wc -l)
echo $original
echo $atual

if [ $original -eq $atual ]
then
mysql -u root -p"$senha" -e "TRUNCATE TABLE telefone" portado
mysql -u root -p"$senha" -e "LOAD DATA LOCAL INFILE '/tmp/telefone.csv'
INTO TABLE telefone
FIELDS TERMINATED BY ';'
LINES TERMINATED BY '\n'
(numero, operadora, @vdata)
SET data = STR_TO_DATE(@vdata, '%d/%m/%Y');" portado

else
   echo 'Local line number differ from the downloaded one, the data was not updated to the database\n'
fi

