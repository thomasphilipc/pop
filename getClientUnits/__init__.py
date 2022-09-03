import logging
import json
import azure.functions as func
import os
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def main(req: func.HttpRequest , inputTable) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    json_response = json.loads(inputTable)
    client=json_response[0]
    logging.info(client)
    if client.get("enabled"):
        tableStorageKey = os.environ["tableStorageKey"]
        tableName = os.environ["tableName"]
        accountName = os.environ["accountName"]
        searchtype=req.params.get("searchtype")
        searchvalue=req.params.get("searchvalue")
        endsearchvalue=searchvalue[:-1]+chr(ord(searchvalue[-1:]) + 1)
        logging.info(searchtype)
        logging.info(searchvalue)
        payload = json.loads(inputTable)
        logging.info("data output from getunitclients  is %s",str(payload))
        table_service = TableService(account_name=accountName, account_key=tableStorageKey)
        table_name = tableName
        query=searchtype+" ge '"+str(searchvalue)+"' and "+searchtype+" le '"+str(endsearchvalue)+"'"
        logging.info(query)
        assets = table_service.query_entities(table_name, filter=query)
        assetlist = []
        for asset in assets:
            assetlist.append(asset)
        assetlistjson=json.dumps(assetlist, indent=4,sort_keys=True, default=str )
        func.HttpResponse.mimetype = 'application/json'
        func.HttpResponse.charset = 'utf-8'
        return func.HttpResponse(assetlistjson)

    else:
        return 403


        
