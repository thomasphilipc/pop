import datetime
import logging
import requests
import azure.functions as func
import json

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Sync timer trigger function ran at %s', utc_timestamp)

    url = "https://vectorglobe.azurewebsites.net/api/orchestrators/DurableOrchestratorG2U"
    #url = "http://localhost:7071/api/orchestrators/DurableOrchestratorG2U"
    payload = ''
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    logging.info(json.loads(response.text.encode('utf8')))
