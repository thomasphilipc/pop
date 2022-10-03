import logging
import json
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import os
import re


def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    #"{\"unit_id\": \"filecontainer/322207.xlsx\", \"htm\": \"HTm123123123123\", \"packing_list\": [\"pl1231231\", \"pl54134123\", \"pl15123123\", \"pl5123132123\"]}"

    json_data=json.loads(msg.get_body().decode('utf-8'))
    logging.info(json_data) 
    json_data=json.loads(json_data)
    unit_id=re.findall(r'\d+', json_data["unit_id"])

    #gather details from the OS environment
    tableStorageKey = os.environ["tableStorageKey"]
    tableName = os.environ["customfieldTableName"]
    accountName = os.environ["accountName"]
    table_service = TableService(account_name=accountName, account_key=tableStorageKey)
    table_name = tableName

    entry = Entity()
    entry.RowKey = str(unit_id[0])
    entry.PartitionKey = "customfield"
    entry.AdditionalField = json.dumps(json_data)
    table_service.merge_entity(table_name,entry)