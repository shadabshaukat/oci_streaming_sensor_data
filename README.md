# Sensor Data Streaming to OCI - Producer

This Python script demonstrates how to generate fake sensor data and stream it to Oracle Cloud Infrastructure (OCI) Streaming service using a producer-consumer pattern.
Description

The script creates two threads, one for generating sensor data (producer) and another for publishing it to the OCI Stream (consumer). The producer generates fake sensor data, simulating temperature and humidity readings from multiple sensors, and stores the data in a queue. The consumer reads the data from the queue and publishes it to the OCI Stream.
Requirements

    Python 3.6 or higher
    OCI Python SDK

Configuration

Before running the script, make sure to configure the following variables in the streaming.py script according to your OCI Streaming service setup:

    ociMessageEndpoint: The OCI streaming service endpoint (e.g., "https://cell-1.streaming.<region>.oci.oraclecloud.com").
    ociStreamOcid: The OCID of the stream (e.g., "ocid1.stream.oc1.*************").
    ociConfigFilePath: The path to your OCI configuration file (e.g., "/home/opc/.oci/config").
    ociProfileName: The name of the profile to use in the OCI configuration file (e.g., "DEFAULT").

Usage

To run the script, execute the following command:

```
python3 streaming_producer.py
```

<img width="1238" alt="Screen Shot 2023-03-15 at 9 02 03 pm" src="https://user-images.githubusercontent.com/39692236/225275632-5be49399-63af-4df0-be9e-96a74bb8792d.png">

The script will continuously generate sensor data and publish it to the OCI Stream.

# Sensor Data Streaming from OCI - Consumer

This script continuously reads sensor data messages from the Oracle Cloud Infrastructure (OCI) Streaming service and is the consumer part of the producer-consumer pattern.

Consumer script reads messages from the OCI Stream using a group cursor and processes them in a continuous loop. It outputs the message offset, key, and value (sensor data) to the screen. The script sleeps for 1 second if there are no messages to process.

To run the script, execute the following command:

```
python3 streaming_consumer.py
```

<img width="1045" alt="Screen Shot 2023-03-16 at 12 24 03 am" src="https://user-images.githubusercontent.com/39692236/225321942-49804a28-cdc6-49ab-8e00-d681145068fe.png">

The consumer script will continuously read messages from the OCI Stream and print the message offset, key, and value (sensor data) to the screen.


# Sensor Data Streaming from OCI - Consume Stream --> Write to ATP

This will read from the OCI Stream and write to a table in Oracle Autonomous Transaction Processing (ATP) Database for doing Time-series analysis

### Create table in ATP

```
CREATE TABLE sensor_data (
    sensor_id VARCHAR2(32) NOT NULL,
    temperature NUMBER(5, 2) NOT NULL,
    humidity NUMBER(5, 2) NOT NULL,
    timestamp TIMESTAMP,
    PRIMARY KEY (sensor_id, timestamp)
);
```

To run the script run the below code :

```
python3 streaming_consumer_atp.py
```
 
Read the data from ATP

```
select count(*) from sensor_data;
```

<img width="625" alt="Screen Shot 2023-03-16 at 1 37 46 am" src="https://user-images.githubusercontent.com/39692236/225343369-aebd2ced-65ee-4cd9-be51-0e45f22fe12d.png">

```
select * from sensor_data where rownum < = 5;
```
<img width="986" alt="Screen Shot 2023-03-16 at 1 38 33 am" src="https://user-images.githubusercontent.com/39692236/225343624-47bb1b59-d34b-430e-9084-b8e183c4da71.png">
