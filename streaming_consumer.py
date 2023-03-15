import oci
import json
from base64 import b64decode
import time
import threading

ociMessageEndpoint = "https://cell-1.streaming.ap-melbourne-1.oci.oraclecloud.com"
ociStreamOcid = "ocid1.stream.oc1.ap-melbourne-1.amaaaaaawiclygaa3l62n6iy2co4kl2bpxw4wrtqg3joncbcirnyphtv7dba"
ociConfigFilePath = "/home/opc/.oci/config"
ociProfileName = "DEFAULT"

def get_cursor_by_group(sc, sid, group_name, instance_name):
    cursor_details = oci.streaming.models.CreateGroupCursorDetails(group_name=group_name, instance_name=instance_name, type="LATEST")
    response = sc.create_group_cursor(sid, cursor_details)
    return response.data.value

def simple_message_loop(client, stream_id, initial_cursor):
    cursor = initial_cursor
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
                print("Message Offset: {}, Key: {}, Value: {}".format(message.offset, key, json.loads(value)))
            # use the next-cursor for iteration
            cursor = get_response.headers["opc-next-cursor"]


def main():
    config = oci.config.from_file(ociConfigFilePath, ociProfileName)
    stream_client = oci.streaming.StreamClient(config, service_endpoint=ociMessageEndpoint)

    group_name = "group1"
    instance_name = "instance1"

    # Get a cursor using a group and instance
    cursor = get_cursor_by_group(stream_client, ociStreamOcid, group_name, instance_name)

    # Read messages using the cursor
    simple_message_loop(stream_client, ociStreamOcid, cursor)

if __name__ == "__main__":
    main()
