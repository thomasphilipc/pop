  # This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json


def main(name: str, clientsJSON) -> str:
    logging.info("data read from database is %s",str(clientsJSON))
    payload = json.loads(clientsJSON)
    logging.info("data output from activitygetgroups is %s",str(payload))
    return payload
