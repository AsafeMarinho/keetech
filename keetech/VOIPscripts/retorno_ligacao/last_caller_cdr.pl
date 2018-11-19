#!/usr/bin/perl -w

# Example data from the table
# +---------------------+-------------+-------------+-------------+
# | calldate            | src         | dst         | disposition |
# +---------------------+-------------+-------------+-------------+
# | 2015-09-07 21:48:24 | 10          | 03199961451 | ANSWERED    | 
# | 2015-09-05 18:37:48 | 10          | 03199961451 | NO ANSWER   | 
# | 2015-09-05 18:35:24 | 10          | 99961451    | NO ANSWER   | 
# | 2015-08-27 14:20:52 | 10          | 99969813    | NO ANSWER   | 
# | 2015-08-24 19:09:02 | 10          | 03199969813 | ANSWERED    | 
# | 2015-08-24 19:08:15 | 10          | 03199961451 | ANSWERED    | 
# | 2015-08-24 19:07:27 | 10          | 03199961451 | ANSWERED    | 
# | 2015-08-24 19:06:48 | 20          | 10          | ANSWERED    | 
# | 2015-08-24 19:06:10 | 10          | 20          | ANSWERED    | 
# | 2015-08-24 18:59:28 | 03199961395 | 20          | ANSWERED    | 
# | 2015-08-24 18:58:43 | 03199961395 | 20          | ANSWERED    | 
# | 2015-08-24 18:58:11 | 03199961395 | 20          | ANSWERED    | 
# | 2015-08-24 18:56:43 | 1000        | 5000        | FAILED      | 
# | 2015-08-24 18:51:26 | 1000        | 5000        | FAILED      | 
# | 2015-08-24 18:44:17 | 1000        | 5000        | FAILED      | 
# | 2015-08-24 18:43:49 | 1000        | 5000        | FAILED      | 
# | 2015-08-24 18:43:12 | 20          | 99961395    | ANSWERED    | 
# +---------------------+-------------+-------------+-------------+

use DBI qw(:sql_types);
use DBD::mysql;

use Asterisk::AGI;

use Getopt::Long;
use warnings;
use strict;

$|=1;

my $database = 'asteriskcdrdb';
my $host = 'localhost';
my $userid = 'asteriskuser';
my $passwd = 'PASSWORD';

chomp ($database, $host, $userid, $passwd);

my $destination_number;
my $position = 0;

if(defined($ARGV[0])){
	$position = $ARGV[0];
}

my $agi       = new Asterisk::AGI;
my %chan_vars = $agi->ReadParse();

$destination_number = substr($chan_vars{'callerid'}, -8);

my $connection = ConnectToMySql($database);

# set the value of your SQL query
my $query = "select calldate, src from cdr where src != '' and dst like ? order by calldate desc LIMIT 1 OFFSET ?";
my $statement = $connection->prepare($query);
$statement->bind_param( 1, '%'.$destination_number );
$statement->bind_param( 2, $position, SQL_INTEGER );

$statement->execute();

my @data = $statement->fetchrow_array();	

print STDERR " LASTCALLER DEBUG -- @data\n";
open(my $fh, '>', '/tmp/lastcaller.txt');
print $fh " LASTCALLER DEBUG -- @data\n";
print $fh " AGI Environment Dump:\n";
foreach my $i (sort keys %chan_vars) {
        print $fh " -- $i = $chan_vars{$i}\n";
}

close $fh;

if($data[0]){
	$agi->set_variable('LAST_CALLER', $data[1]);
}
else{
	$agi->set_variable('LAST_CALLER', '');
}

# exit the script
exit;

#--- start sub-routine ------------------------------------------------
sub ConnectToMySql {
#----------------------------------------------------------------------

my ($db) = @_;

# assign the values to your connection variable
my $connectionInfo="dbi:mysql:$db;$host";

# make connection to database
my $l_connection = DBI->connect($connectionInfo,$userid,$passwd);

# the value of this connection is returned by the sub-routine
return $l_connection;

}

#--- end sub-routine --------------------------------------------------
