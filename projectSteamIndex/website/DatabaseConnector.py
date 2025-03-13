import pandas as pd
from mysql.connector import errorcode
import mysql.connector


class DatabaseConnector:
    def __init__(self):
        self.db_name = "testdb"
        self.db_host = "localhost"
        self.db_username = "kkhatra"
        self.db_password = "password"
        self.cnx = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(
                user=self.db_username,
                password=self.db_password,
                host=self.db_host,
                database=self.db_name
            )
            self.cursor = self.cnx.cursor()
            print("Connected!")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def query(self, query, params=None):
        if self.cursor:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()

    def query_dataframe(self, query, params=None):
        if self.cursor:
            self.cursor.execute(query, params or ())
            columns = [desc[0] for desc in self.cursor.description]
            data = self.cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            return df

    def insert(self, insert_query, params):
        try:
            if self.cursor:
                self.cursor.execute(insert_query, params)
                self.cnx.commit()
                print("Insert successful!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print(params)
            self.cnx.rollback()

    def delete(self, delete_query, params=None):
        try:
            if self.cursor:
                self.cursor.execute(delete_query, params or ())
                self.cnx.commit()
                print("Delete successful!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.cnx.rollback()

    def update(self, update_query, params):
        try:
            if self.cursor:
                self.cursor.execute(update_query, params)
                self.cnx.commit()
                print("Update successful!")
        except mysql.connector.Error as err:
            print(f"Errorss: {err}")
            self.cnx.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.cnx:
            self.cnx.close()
        print("Closed connection")

