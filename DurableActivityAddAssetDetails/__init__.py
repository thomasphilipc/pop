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


def process_response(payload,assetgroup):
    jsondata=json.dumps(payload)
    responselist=[]
    logging.info(json.loads(jsondata))
    units_list=(json.loads(jsondata)).get("data")
    for this_item in units_list.get("units"):
        logging.info(this_item)
        item=json.loads(json.dumps(this_item))
        entry = Entity()
        entry.RowKey = str(item['unit_id'])
        entry.PartitionKey = str(item['company_id'])
        entry.country_code = str(item['country_code'])
        entry.label = str(item['label'])
        entry.assetName = str(item['number'])
        entry.lat= item['lat']
        entry.lon = item['lng']
        entry.clientName=assetgroup
        entry.direction = item['direction']
        entry.speed = item['speed']
        entry.last_update = item['last_update']
        entry.created_at = item['created_at']
        entry.imei = str(item.get('device').get('imei')) if item.get('device') else "Not Available"
        entry.boxId = str(item.get('device').get('id')) if item.get('device') else "Not Available"
        #entry.companyName = item
        responselist.append(entry)
    
    return responselist

async def main(result2: str) -> str:
    tableStorageKey = os.environ["tableStorageKey"]
    tableName = os.environ["tableName"]
    accountName = os.environ["accountName"]
    logging.info( " data recieved in durable activityaddassetgroup is format %s",str(result2))
    assetgroup=result2['clientName']
    endpoint = "https://mapon.com/"
    path = "api/v1/unit/list.json?include=device&key="+result2['apiKey']
    params=""
    total_units=result2["units"]
    if len(total_units)>0:
        for i in result2["units"]:
            params+="&unit_id[]="+str(i)
        
        constructed_url = endpoint + path + params

        headers = {

        "Content-Type": "application/json"
        }
        client = httpx.AsyncClient()
        response = await client.get(constructed_url, headers = headers)
        payload = response.json()
        data=process_response(payload,assetgroup)

        table_service = TableService(account_name=accountName, account_key=tableStorageKey)
        table_name = tableName
        # research batch insert to handle gracefully
        for item in data:
            logging.info(" data to be pushed into database is %s",str(item))
            table_service.insert_or_replace_entity(table_name,item)

        return f"Devices have been added and no output at this stage for{assetgroup}"
    else:
         return f"No Devices have been added and no output at this stage for{assetgroup}"
