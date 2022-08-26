import logging
import json
import httpx
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity


async def main(msg: func.QueueMessage) -> None:
    logging.info("adding trigger for units")


    payload=json.loads(msg.get_body())    
    endpoint = "https://mapon.com/"
    path = "api/v1/unit/list.json?key="+payload['apiKey']
    params=""
    for i in payload["units"]:
        params+="&unit_id[]="+str(i)
    
    constructed_url = endpoint + path + params

    headers = {

       "Content-Type": "application/json"
    }

    client = httpx.AsyncClient()
    response = await client.get(constructed_url, headers = headers)
    payload = response.json()
    data=process_response(payload)
    
    table_service = TableService(account_name='pop2022', account_key='fQOMjjZSKI5wAUv/sOFAz6i4tAXbBXGE+az+tYnWyqapI2jIihSERhP9Cb+Yd4v+dmob9HmvlFw5+ASt8xoKQQ==')
    table_name = 'assetTable'
    for item in data:
        table_service.insert_or_replace_entity(table_name,item)

def process_response(payload):
    jsondata=payload
    responselist=[]
    for item in jsondata['data']['units']:
        entry = Entity()
        entry.RowKey = str(item['unit_id'])
        entry.PartitionKey = str(item['company_id'])
        entry.country_code = item['country_code']
        entry.label = item['label']
        entry.assetName = item['number']
        entry.lat= item['lat']
        entry.lon = item['lng']
        entry.direction = item['direction']
        entry.speed = item['speed']
        entry.last_update = item['last_update']
        entry.created_at = item['created_at']
        #asset_data = {'RowKey': item['unit_id'], 'PartitionKey': item['company_id'], 'country_code': item['country_code'],
        #            'label': item['label'], 'number': item['number'], 'lat': item['lat'], 'lng': item['lng'],
        #            'direction': item['direction'], 'speed': item['speed'], 'last_update': item['last_update'],
        #            'created_at': item['created_at']}
        responselist.append(entry)
    
    
    
    return responselist




