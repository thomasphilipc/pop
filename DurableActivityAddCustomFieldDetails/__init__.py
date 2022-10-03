# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import httpx
import json
import os
import re
import azure.functions as func

def process_field_type(data):
    item=data
    label=re.sub(r'\W+', '', item["label"])
    #logging.info( " data recieved in durable process_response/process_response/process_field_type data is format %s",str(data))
    if item["type"]=="select":
        # have to do custom stuff to return the name of the option to handle options
        return {label: item["settings"]["options"][item["value"]]} if item["value"] else {label: item["value"]}
    else:
        return {label: item["value"]}

def process_response(payload,schema_json,i):

    ######
    #logging.info( " data recieved in durable activityaddcustomfield/process_response is format %s",str(payload))
    schema_keys=schema_json.keys()
    entry = Entity()
    # save the RowKey as unit_id abd PartitiionKey as customfield
    entry.RowKey = str(i)
    entry.PartitionKey = "customfield"
    return_dict={}  
    for item in payload["data"]:
        if item["label"] in schema_keys:
            value=process_field_type(item)
            return_dict.update(value)


    entry.CustomField= json.dumps(return_dict)

    return entry

    ######


async def main(result2: str, changemanagementqueue: func.Out[str]) -> str:
    
    #gather details from the OS environment
    tableStorageKey = os.environ["tableStorageKey"]
    tableName = os.environ["customfieldTableName"]
    accountName = os.environ["accountName"]
    table_service = TableService(account_name=accountName, account_key=tableStorageKey)
    table_name = tableName

    # what is the data that is passed to through the function
    #logging.info( " data recieved in durable activityaddcustomfield data is format %s",str(result2))
    #gathering the schema
    schema_text=result2['customField'].replace("'",'''"''')
    # possiblility for error on the line above
    schema_json=json.loads(schema_text)
    endpoint = "https://mapon.com/"
    path = "api/v1/unit/custom_fields.json?include=device&key="+result2['apiKey']
    response_list=[]
    for i in result2["units"]:
        params="&unit_id="+str(i)
        constructed_url = endpoint + path + params
        headers = {

       "Content-Type": "application/json"
        }
        client = httpx.AsyncClient()
        response = await client.get(constructed_url, headers = headers)
        payload = response.json()
        data=process_response(payload,schema_json,i)
        query="RowKey eq '"+str(i)+"'"
        ###
        test = []
        for entity in table_service.query_entities(table_name, filter=query):
            test.append(entity)
        test = json.dumps(test, indent=4, sort_keys=True, default=str)
        db_data = json.loads(test)[0]
        ###
        #'{"PackageType": null, "PackingListUpload": null, "TrackingLink": null}'
        if db_data['CustomField']!= data['CustomField']:
            logging.info(" data variation and to be addded to list %s",str(data))
            response_list.append(data)


    #logging.info(" data to be pushed into database is %s",str(data))
    for data in response_list:
        changemanagementqueue.set(json.dumps(data, indent=4, sort_keys=True, default=str))
        table_service.insert_or_replace_entity(table_name,data)
    return "Devices have been added and no output at this stage"
    
    
    #below cannot be done on a single call and needs to be split to different calls and processed individually


    



