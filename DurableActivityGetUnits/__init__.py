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




def main(payload) -> str:
    logging.info( " data  in durable activityGetUnits is format %s",str(payload))
    #payload=json.dumps(payload)
    group_id= payload['RowKey']
    apikey=payload['apiKey']
    units=get_units(group_id,apikey)
    payload['units']=units
    return payload


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
    logging.info( " data  output in durable activityGetUnits is format %s",str(total_units))
    return (total_units)
