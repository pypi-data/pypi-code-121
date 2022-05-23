import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()


def connect():
    try:
        conn = mysql.connector.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("HOST"),
            port=3306,
            database=os.getenv("DB"),
            ssl_ca="{ca-cert filename}",
            ssl_disabled=False,
        )
        if conn.is_connected():
            print("Connection to database established")
            return conn

    except Error as e:
        print("Error while connecting to MySQL", e)
