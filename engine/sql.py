import mysql.connector
from mysql.connector import Error
# import pandas as pd

def create_db_connection(host_name, user_name, user_password, db_name = ""):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        print("Query {} connection successful".format(query))
        return result
    except Error as err:
        print(f"Error: '{err}' query: {query}")


def execute_file(connection, file):
    cursor = connection.cursor()
    try:
        for line in open(file):
            cursor.execute(line)
            connection.commit()
            print(line)
    except Error as err:
        print(f"Error: '{err}'")

def execute_list_query(connection, sql, val):
    cursor = connection.cursor()
    try:
        cursor.executemany(sql, val)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

conn = create_db_connection("localhost", "root", "qweRtY1576")
if (conn):
    execute_query(conn, "select count(*) from creds")
else:
    print("failed to connect")
# conn = create_db_connection("localhost", "root", "1")
# execute_file(conn, "db_init.sql")
