import logging
from sre_constants import SUCCESS
import uuid
import json
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import azure.functions as func
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    


    req_body = req.get_json()
    logging.info(req_body)
    clientName = req_body.get('clientName')
    clientKey = req_body.get('clientKey')
    apiKey = req_body.get('apiKey')
    group = req_body.get('group')
    clientId = req_body.get('clientId')
    enabled = req_body.get('enabled')
    alert_enabled = req_body.get("process_alerts")


    tableStorageKey = os.environ["tableStorageKey"]
    tableName = os.environ["clienttableName"]
    accountName = os.environ["accountName"]

    entry = Entity()
    entry.RowKey = str(group)
    entry.PartitionKey = str(clientId)
    entry.apiKey = apiKey
    entry.clientKey = clientKey
    entry.clientName = clientName
    entry.enabled = enabled
    entry.process_alerts = alert_enabled
    
    table_service = TableService(account_name=accountName, account_key=tableStorageKey)
    table_service.insert_or_replace_entity(tableName,entry)



    return func.HttpResponse(f"saved: {json.dumps(entry)}")


            


   