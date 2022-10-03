import logging
import pandas as pd
import azure.functions as func
from io import BytesIO
import json

def main(myblob: func.InputStream, additionaldataqueue: func.Out[str]):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    blob_to_read = myblob.read()
    df = pd.read_excel(blob_to_read)
    unit_id=myblob.name
    column_headers = list(df.columns.values)
    htm = column_headers[0]
    values=list(df[htm])
    return_dict = {'unit_id': unit_id, 'htm': htm, 'packing_list': values}
    return_json = json.dumps(return_dict)

    logging.info(return_json)
    additionaldataqueue.set(json.dumps(return_json))
    
