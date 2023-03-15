# Sensor Data Streaming to Oracle Cloud Infrastructure Streaming

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
python3 streaming.py
```

The script will continuously generate sensor data and publish it to the OCI Stream.


<img width="1238" alt="Screen Shot 2023-03-15 at 9 02 03 pm" src="https://user-images.githubusercontent.com/39692236/225275632-5be49399-63af-4df0-be9e-96a74bb8792d.png">
