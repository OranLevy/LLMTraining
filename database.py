import mysql.connector
from mysql.connector.locales.eng import client_error
import config
from typing import Literal


class Database:
    connection = None

    def __init__(self, db_name, instance: Literal["move_cx_1", "travelyo"]):
        if instance == "move_cx_1":
            self.connection = mysql.connector.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=db_name,
            )
        else:
            self.connection = mysql.connector.connect(
                host=config.DB_TRAVELYO_HOST,
                user=config.DB_TRAVELYO_USER,
                password=config.DB_TRAVELYO_PASSWORD,
                database=db_name,
            )

    def query(self, sql, args=""):
        cursor = self.connection.cursor()
        cursor.execute(sql, args)
        return cursor

    def insert(self, sql, args=""):
        cursor = self.query(sql, args)
        id = cursor.lastrowid
        self.connection.commit()
        return id

    def insertmany(self, sql, val=""):
        cursor = self.connection.cursor()
        cursor.executemany(sql, val)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount

    def update(self, sql, args=""):
        cursor = self.query(sql, args)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount

    def fetch(self, sql, args=""):
        rows = []
        cursor = self.query(sql, args)
        if cursor.with_rows:
            rows = cursor.fetchall()
        cursor.close()
        return rows

    def fetchone(self, sql, args):
        row = None
        cursor = self.query(sql, args)
        if cursor.with_rows:
            row = cursor.fetchone()
        cursor.close()
        return row

    # def __del__(self):
    #     if self.connection is not None:
    #         self.connection.close()
