#!/bin/sh

set -e

db_host="$1"
db_port="$2"
db_password="$3"
shift 3
cmd="$@"

#python /opt/social_net/wait_for_mysql.py -h $db_host -P $db_port -p $db_password -d $db_name
until mysql -P ${db_port} --host=${db_host} --protocol=tcp --password=${db_password} --user=root
do
    echo "sleep..."
    sleep 1
done

echo "done"
exec $cmd
