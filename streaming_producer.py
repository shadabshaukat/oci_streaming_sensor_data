import oci
import json
from base64 import b64encode
import random
from datetime import datetime, timedelta
import time
import threading
import queue

ociMessageEndpoint = "https://cell-1.streaming.ap-melbourne-1.oci.oraclecloud.com"
ociStreamOcid = "ocid1.stream.oc1.ap-melbourne-1.amaaaaaawiclygaa3l62n6iy2co4kl2bpxw4wrtqg3joncbcirnyphtv7dba"
ociConfigFilePath = "/home/opc/.oci/config"
ociProfileName = "DEFAULT"

def produce_messages(client, stream_id, input_json):
    key = input_json["sensor_id"]
    value = json.dumps(input_json)

    encoded_key = b64encode(key.encode()).decode()
    encoded_value = b64encode(value.encode()).decode()

    message = oci.streaming.models.PutMessagesDetailsEntry(key=encoded_key, value=encoded_value)

    print("Publishing message to the stream {} ".format(stream_id))
    messages = oci.streaming.models.PutMessagesDetails(messages=[message])
    put_message_result = client.put_messages(stream_id, messages)

    for entry in put_message_result.data.entries:
        if entry.error:
            print("Error ({}) : {}".format(entry.error, entry.error_message))
        else:
            print("Published message to partition {} , offset {}".format(entry.partition, entry.offset))

# Producer function to generate fake sensor data and put it in the queue
def generate_sensor_data(sensor_data_queue):
    while True:
        sensor_id = "s{:03d}".format(random.randint(1, 100))
        temperature = round(random.uniform(60, 100), 2)
        humidity = round(random.uniform(30, 70), 2)
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        record = {
            "sensor_id": sensor_id,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": timestamp
        }

        sensor_data_queue.put(record)
        time.sleep(1)  # Adjust the sleep duration to control the rate of data generation

# Consumer function to read sensor data from the queue and publish it to OCI Stream
def publish_to_oci_stream(sensor_data_queue):
    config = oci.config.from_file(ociConfigFilePath, ociProfileName)
    stream_client = oci.streaming.StreamClient(config, service_endpoint=ociMessageEndpoint)

    while True:
        record = sensor_data_queue.get()
        produce_messages(stream_client, ociStreamOcid, record)

def main():
    sensor_data_queue = queue.Queue()

    # Create and start producer and consumer threads
    producer_thread = threading.Thread(target=generate_sensor_data, args=(sensor_data_queue,))
    consumer_thread = threading.Thread(target=publish_to_oci_stream, args=(sensor_data_queue,))

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

if __name__ == "__main__":
    main()
