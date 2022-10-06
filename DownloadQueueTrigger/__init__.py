import logging
import os
import uuid
import time
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


def main(msg: func.QueueMessage) -> None:
    logging.info('Download queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    #data incoming sample
    #{
    #"CustomField": "{\"PackageType\": \"type 2\", \"PackingListUpload\": \"https://mapon.com/file.php?6292547$c0099b9a0451d6202d3bb5\", \"TrackingLink\": \"http://please.com\"}",
    #"PartitionKey": "customfield",
    #"RowKey": "322207"
    #}
    #obtain link from the queue
    queue_payload=msg.get_body().decode('utf-8')
    ####
    json_data=json.loads(queue_payload)
    json_customfield=json.loads(json_data["CustomField"])
    ####
    #{
    #"CustomField": "{"PackageType": "type 2", "PackingListUpload": "https://mapon.com/file.php?6292547$c0099b9a0451d6202d3bb5", "TrackingLink": "http://please.com"}",
    #"PartitionKey": "customfield",
    #"RowKey": "322207"
    #}
    unit_id=json_data.get("RowKey")
    link=json_customfield.get("PackingListUpload")
    # expects to recieve only unit_id and link only if the file is updated from the one on database
    # this will proceed to download the file and rename the file with unit_id.xlsx
    # to do - need to create the filename with the unit_id.xlsx
    filename=unit_id+".xlsx"
    process_link(link,filename)


def process_link(link,filename):
    try:
        CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    except KeyError:
        logging.critical("AZURE_STORAGE_CONNECTION_STRING must be set.")
        

    status = None
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    source_blob = link
    copied_blob = blob_service_client.get_blob_client("filecontainer", filename)
    # Copy started
    copied_blob.start_copy_from_url(source_blob)
    for i in range(10):
        props = copied_blob.get_blob_properties()
        status = props.copy.status
        print("Copy status: " + status)
        if status == "success":
            # Copy finished
            break
        time.sleep(10)

    if status != "success":
        # if not finished after 100s, cancel the operation
        props = copied_blob.get_blob_properties()
        logging.info(props.copy.status)
        copy_id = props.copy.id
        copied_blob.abort_copy(copy_id)
        props = copied_blob.get_blob_properties()
        logging.info(props.copy.status)

