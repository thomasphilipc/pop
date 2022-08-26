import logging
import requests
import json
import azure.functions as func


def main(msg: func.QueueMessage, clientUnits: func.Out[str]) -> None:
    logging.info('Processed queue')
    payload=json.loads(msg.get_body())    
    group_id= payload['group']
    apikey=payload['apiKey']
    units=get_units(group_id,apikey)
    payload['units']=units
    clientUnits.set(json.dumps(payload))


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
    logging.info(responserecvd)
    list_list = responserecvd["data"]
    unit_ids = list_list
    if(unit_ids['units']):
        for unit in unit_ids['units']:
            total_units.append(unit['id'])
    return (total_units)