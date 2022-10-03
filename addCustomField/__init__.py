import logging
import requests
import azure.functions as func
import json
import os
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def main(req: func.HttpRequest, inputTable, customfieldTable: func.Out[str]) -> func.HttpResponse:
    try:
        #response to the query where client picked with api lookup
        json_response = json.loads(inputTable)
        # expecting only one value
        logging.info(json_response[0])
        # checking if the API service is enabled for the user
        if json_response[0].get("enabled"):
            #gathering the schema data from the client master table
            cusom_field_schema = json_response[0].get("customField")
            #{'Text Field': {'id': 2526195, 'settings': []}, 'Date Field': {'id': 2526196, 'settings': []}, 'File Field': {'id': 2526197, 'settings': []}, 'Link Field': {'id': 2526198, 'settings': []}, 'Image Field': {'id': 2526199, 'settings': []}, 'Select Field': {'id': 2526201, 'settings': {'options': {'632cd078c5e3e': 'option 1', '632cd078c5e40': 'option 2', '632cd078c5e41': 'option 3'}}}}
            schema=json.load(cusom_field_schema)
            #use the schema to lookup the value that needs to be pushed to asset

            #getting the neccesary connections and data to gather the asset details from the asset master table
            tableStorageKey = os.environ["tableStorageKey"]
            tableName = os.environ["tableName"]
            accountName = os.environ["accountName"]
            table_service = TableService(account_name=accountName, account_key=tableStorageKey)
            table_name = tableName
            
            # reading the json value recieved from user 
            req_body = req.get_json()
            logging.info(req_body)
            #get the data from the expected format
            json_dict = json.loads(req_body)
            #get the keys assuming there is atleast 1 entry
            keys = json_dict["data"][0].keys()
            #cycle through each entry assuming they have provided more than one value
            if (len(json_dict["data"])) > 0:
                for item in json_dict["data"]:
                    print ("process each item")
                    for key in keys:
                        #process each key - how can this be prcoessed ?
                        logging.info(req_body)("process each value {}".format(item[key]))
                    #get unitid as row key    
                    unit_id = item['unit_id']    
                    # use schema to create entry
                    data = {
                    "PartitionKey": unit_id,
                    "RowKey": "customfield",
                    "customfield" : {}
                     }

                    #save to database    
                    customfieldTable.set(json.dumps(data))

            return func.HttpResponse(f"saved: {data}")

    except ValueError:
        pass
            




    return func.HttpResponse(
             "This data has been saved.",
             status_code=200
        )

# how to write custom fields to Mapon.
def write_custom_field(values,record):

    url = "https://www.mapon.com/api/v1/unit/save_custom_fields_values.json"

    payload={'key': '3713dd8c788ab7cc06ccf0af82713e7260cec63d',
    'unit_id': '270610',
    'fields[2526195]': 'new sample',
    'fields[2526196]': '1666476831',
    'fields[2526198]': '{"title":"this","value":"that"}',
    'fields[2526199]': '{"value":"https://vectorglobe.com/wp-content/uploads/2019/05/cropped-VectorGlobe_RGB_small-1-1.png"}',
    'fields[2526201]': '632cd078c5e40',
    'fields[2526198]["value"]': 'https://vectorglobe.com'}
    files=[
    ('fields[2526199]',('12th Standard.jpeg',open('/C:/Users/talk2/Downloads/12th Standard.jpeg','rb'),'image/jpeg'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)
