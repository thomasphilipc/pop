import datetime
import logging
import json
import typing

import azure.functions as func


def main(mytimer: func.TimerRequest, clientsJSON, msg: func.Out[typing.List[str]]  ) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')


    list=json.loads(clientsJSON)
    msg.set(json.dumps(list))
    logging.info('Python timer trigger function and got %s', clientsJSON)

