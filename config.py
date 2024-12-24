import boto3
import os
import json

#  Local credentials
region_name = "eu-central-1"
session = boto3.session.Session()
client = session.client(service_name="secretsmanager", region_name=region_name)
cx_db_admin_user = json.loads(
    client.get_secret_value(SecretId="cx_db/admin_user")["SecretString"]
)
db_travelyo_master = json.loads(
    client.get_secret_value(SecretId="travelyo_master_v4")["SecretString"]
)
DB_HOST = cx_db_admin_user["host"]
DB_PASSWORD = cx_db_admin_user["password"]
DB_USER = cx_db_admin_user["username"]
DB_TRAVELYO_HOST = "db-ws.smartair.co.il"
DB_TRAVELYO_USER = db_travelyo_master["user"]
DB_TRAVELYO_PASSWORD = db_travelyo_master["password"]

