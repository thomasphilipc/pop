# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json
import requests
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import os



def main(payload) -> str:
    logging.info( " data  in durable activityGetUnits is format %s",str(payload))
    #payload=json.dumps(payload)
    group_id= payload['RowKey']
    apikey=payload['apiKey']
    units=get_units(group_id,apikey)
    payload['units']=units
    payload['total_units']=len(units) if units else 0
    # add custom field if available
    if units:
        customField=get_custom_field(units[0],apikey)
        payload['customField']=customField
    else:
        payload['customField']=None

    # save to database
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





def get_units(group_id,apikey):

    total_units = []

    url = "https://mapon.com/api/v1/unit_groups/list_units.json?key="+str(apikey)+"&id=" + str(group_id)
    logging.info(url)
    payload = ''
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    responserecvd = json.loads(response.text.encode('utf8'))
    try:
        unit_ids = responserecvd["data"]

        if(unit_ids['units']):
            for unit in unit_ids['units']:
                total_units.append(unit['id'])

        return (total_units)
    except:
        return(None)
