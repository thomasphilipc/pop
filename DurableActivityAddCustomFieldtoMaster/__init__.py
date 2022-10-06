
import logging
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import httpx
import json
import os
import requests



def main(payload) -> str:
    #payload=json.dumps(payload)
    group_id= payload['RowKey']
    apikey=payload['apiKey']
    unit_id,total_units=get_first_unit(group_id,apikey)
    if unit_id == None:
        logging.info( "No units in group hence cant get custom fields")
    else:
        payload['units']= total_units
        payload['total_units']=len(total_units)
        customField=get_custom_field(unit_id,apikey)
        payload['customField']=customField
        saveToClientTable(payload)

    return payload

def saveToClientTable(payload):


    logging.info( " data  got to save to clientable is format %s",str(type(payload)))
    tableStorageKey = os.environ["tableStorageKey"]
    tableName = os.environ["clienttableName"]
    accountName = os.environ["accountName"]
    logging.info( " data recieved to save is  %s",str(payload))
    entry = Entity()
    entry.RowKey = str(payload.get('RowKey'))
    entry.PartitionKey = str(payload.get('PartitionKey'))
    entry.total_units = str(payload.get('total_units',0))
    unit_list= []
    for item in (payload.get('units',None)):
        unit_list.append(str(item))
    entry.units =  str(unit_list)
    entry.customField = str(payload.get('customField'))
    table_service = TableService(account_name=accountName, account_key=tableStorageKey)
    table_name = tableName
    table_service.insert_or_merge_entity(table_name,entry)
    return "Devices have been added and no output at this stage"


def get_first_unit(group_id,apikey):
    total_units = []
    url = "https://mapon.com/api/v1/unit_groups/list_units.json?key="+str(apikey)+"&id=" + str(group_id)

    payload = ''
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    logging.info(str(response.text.encode('utf8')))
    responserecvd = json.loads(response.text.encode('utf8'))
    try:
        unit_ids = responserecvd["data"]
        if (unit_ids['units']):
            for unit in unit_ids['units']:
                total_units.append(unit['id'])
        return(total_units[0],total_units)
    except:
        return (None,None)

def get_custom_field(unit_id,apikey):
    url = "https://mapon.com/api/v1/unit/custom_fields.json?key="+str(apikey)+"&unit_id=" + str(unit_id)

    payload = ''
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    responserecvd = json.loads(response.text.encode('utf8'))
    cf_asset = responserecvd['data']
    for item in cf_asset:
        try:
            del item['value']
        except KeyError:
            pass
    custom_field={}
    for item in cf_asset:
        custom_field[item['label']]= { "id" : item['id'] , "settings" : item.pop('settings', 'Not Found')}
    return custom_field


