# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json
import time
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

def process_link(link,filename):
    try:
        CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    except KeyError:
        logging.critical("AZURE_STORAGE_CONNECTION_STRING must be set.")
        
    try:
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
                return "File copied"
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
    except:
        return "Error in copying file require for processing"

def main(name: str) -> str:

    logging.info(name)
    print(name)
    #data incoming sample
    #{
    #"CustomField": "{\"PackageType\": \"type 2\", \"PackingListUpload\": \"https://mapon.com/file.php?6292547$c0099b9a0451d6202d3bb5\", \"TrackingLink\": \"http://please.com\"}",
    #"PartitionKey": "customfield",
    #"RowKey": "322207"
    #}
    #obtain link from the queue
    ####
    json_data=json.loads(name)
    json_customfield=json.loads(json_data["CustomField"])

    unit_id=json_data.get("RowKey")
    link=json_customfield.get("PackingListUpload")

    filename=unit_id+".xlsx"
    result= process_link(link,filename)
    
    return f" {result}!"

