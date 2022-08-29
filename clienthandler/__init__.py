import logging
from sre_constants import SUCCESS
import uuid
import json


import azure.functions as func


def main(req: func.HttpRequest, clientTable: func.Out[str]) -> func.HttpResponse:
    

    try:
        req_body = req.get_json()
        logging.info(req_body)
        clientName = req_body.get('clientName')
        clientKey = req_body.get('clientKey')
        apiKey = req_body.get('apiKey')
        group = req_body.get('group')
        clientId = req_body.get('clientId')
        enabled = req_body.get('enabled')

    except ValueError:
        pass
            


    data = {
        "PartitionKey": clientId,
        "RowKey": group,
        "apiKey" : apiKey,
        "clientKey" : clientKey,
        "clientName" : clientName,
        "enabled" : enabled
    }

    
    clientTable.set(json.dumps(data))



    return func.HttpResponse(f"saved: {data}")
