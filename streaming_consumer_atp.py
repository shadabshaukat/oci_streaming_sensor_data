import oci
import time
import json
from base64 import b64decode
import oracledb as cx_Oracle

ociMessageEndpoint = "https://cell-1.streaming.ap-melbourne-1.oci.oraclecloud.com"
ociStreamOcid = "ocid1.stream.oc1.ap-melbourne-1.amaaaaaawiclygaa3l62n6iy2co4kl2bpxw4wrtqg3joncbcirnyphtv7dba"
ociConfigFilePath = "/home/opc/.oci/config"
ociProfileName = "DEFAULT"

# Oracle Database connection details
db_username = "admin"
db_password = "RAbbithole1234#_"
db_dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.ap-melbourne-1.oraclecloud.com))(connect_data=(service_name=g9b8049aad9c64c_y16fuv7vqq9428l5_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"  # Connection string or TNS name for the Oracle Database

def get_cursor_by_group(sc, sid, group_name, instance_name):
    cursor_details = oci.streaming.models.CreateGroupCursorDetails(group_name=group_name, instance_name=instance_name, type="LATEST")
    response = sc.create_group_cursor(sid, cursor_details)
    return response.data.value

def insert_sensor_data(connection, sensor_data):
    insert_sql = '''
    INSERT INTO sensor_data (sensor_id, temperature, humidity, timestamp)
    VALUES (:sensor_id, :temperature, :humidity, TO_TIMESTAMP(:timestamp, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'))
    '''

    cursor = connection.cursor()
    cursor.execute(insert_sql, sensor_data)
    connection.commit()
    cursor.close()

def simple_message_loop(client, stream_id, initial_cursor):
    cursor = initial_cursor
    connection = cx_Oracle.connect(user=db_username, password=db_password, dsn=db_dsn)

    while True:
        get_response = client.get_messages(stream_id, cursor, limit=10)
        # No messages to process. Sleep for a while and try again later.
        if not get_response.data:
            time.sleep(1)
        else:
            # Process the messages
            for message in get_response.data:
                key = b64decode(message.key.encode()).decode()
                value = b64decode(message.value.encode()).decode()
                sensor_data = json.loads(value)
                print("Message Offset: {}, Key: {}, Value: {}".format(message.offset, key, sensor_data))
                insert_sensor_data(connection, sensor_data)

            # use the next-cursor for iteration
            cursor = get_response.headers["opc-next-cursor"]

    connection.close()

def main():
    config = oci.config.from_file(ociConfigFilePath, ociProfileName)
    stream_client = oci.streaming.StreamClient(config, service_endpoint=ociMessageEndpoint)

    group_name = "group1"
    instance_name = "instance1"

    cursor = get_cursor_by_group(stream_client, ociStreamOcid, group_name, instance_name)
    simple_message_loop(stream_client, ociStreamOcid, cursor)

if __name__ == "__main__":
    main()
