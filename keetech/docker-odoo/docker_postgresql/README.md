deltaos-docker-postgresql
=======================

Variáveis de Ambiente

$POSTGRES_PASS - Senha para o usuário 'postgres'
$POSTGRES_NEWUSER - Novo usuário a criar no PostgreSQL a ser usado pelo Odoo
$NEWUSER_PASS - Senha do novo usuário



Imagem do docker para executar um servidor de banco de dados PostgreSQL


Instruções de Uso
-----

Para cria a imagem execute o comando abaixo:

	docker build -t nome_da_imagem .

Para iniciar um container e vincular a porta 5432 execute o comando abaixo:

	docker run -d -p 5432:5432 nome_da_imagem

A primeira vez que você executa o container, um novo usuário `postgres` com todos os privilégios
Será criado no PostgreSQL com uma senha aleatória. Para obter a senha, verifique os logs
Do recipiente rodando:

	docker logs <CONTAINER_ID>

Você verá uma saída como a seguinte:

	========================================================================
	You can now connect to this PostgreSQL Server using:

	    psql -h <host> -p <port> --username=postgres
	and enter the password 'HHrUZyI6ubWF' when prompted

	Please remember to change the above password as soon as possible!
	========================================================================

Nesse caso, `HHrUZyI6ubWF` é a senha atribuída ao usuário` postgres`.



Definir uma palavra-passe específica para a conta de administrador
------------------------------------------------------------------

Se você quiser usar uma senha predefinida em vez de uma gerada aleatoriamente, você pode
definir a variável de ambiente `POSTGRES_PASS` para a sua senha específica ao executar o contêiner:

	docker run -d -p 5432:5432 -e POSTGRES_PASS="mypass" nome_da_imagem


Para conectar ao PostgreSQL do conteiner digite:

        psql -h ip_do_conteiner -U postgres

  **Será solicitada a senha


-------------------------------------------------------------------
Comando para criar um novo usuário no PostgreSQL pelo PSQL

CREATE USER nomedousuario SUPERUSER INHERIT CREATEDB CREATEROLE; 

Comando para alterar/criar senha de novo usuário no PostgreSQL pelo PSQL

ALTER USER nomedousuario PASSWORD 'senha';
