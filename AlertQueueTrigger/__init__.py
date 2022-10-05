import logging
import json
import azure.functions as func
import os
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import smtplib 
import ssl


def send_mail(to_email,message, from_email='helpdesk@vectorglobe.com'):
    # import smtplib
    email_password = os.environ["email_password"]
    email_username = os.environ["email_username"]
    context = ssl.create_default_context()
    port=587
    req_message = message.encode('utf-8')

    smtp_server= os.environ["smtp_server"]
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(email_username, email_password)
        server.sendmail(from_email, to_email, req_message)



def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

  #{
  #"unit_id": 101545,
  #"time": "2022-10-04T01:39:55Z",
  #"alert_type": "speeding",
  #"alert_val": "{\"source\":\"manual\",\"speed\":82,\"speed_limit\":80,\"overspeed_limit\":0}",
  #"msg": "Driving speed is 82 km/h (Manual speed limit: 80 km/h)",  
  #"address": "Līči, Krapes pag., Ogres nov., Latvija",
  #"location": "56.71888,25.20018"
  #}

    data=json.dumps(msg.get_body().decode('utf-8'))
    json_data=json.loads(json.loads(data))

    logging.info(json_data)

    tableStorageKey = os.environ["tableStorageKey"]
    assettableName = os.environ["tableName"]
    accountName = os.environ["accountName"] 
    customfieldTableName = os.environ["customfieldTableName"]
    unit_id=str(json_data["unit_id"])
    table_service = TableService(account_name=accountName, account_key=tableStorageKey)
    query="RowKey eq'"+str(unit_id)+"'"
    assets = table_service.query_entities(assettableName, filter=query)
    asset_det =json.dumps(assets, indent=4,sort_keys=True, default=str )
    assetsc = table_service.get_entity(customfieldTableName, row_key=unit_id, partition_key="customfield")
    for item in assets:
        asset_det_s = json.dumps(item, indent=4,sort_keys=True, default=str )
    asset_det=json.loads(asset_det_s)
    assetscf=json.loads(json.dumps(assetsc, indent=4,sort_keys=True, default=str))
    logging.info(asset_det)
    logging.info(assetscf)
    goods_det = json.loads(assetscf.get("AdditionalField",None))
    cf_det = json.loads(assetscf.get("CustomField",None))
    #{
    #"PartitionKey": "8180",
    #"RowKey": "50043",
    #"Timestamp": "2022-10-03 00:37:33.835730+00:00",
    #"assetName": "SM-55",
    #"boxId": "207568",
    #"clientName": "VectorGlobe Fe+",
    #"country_code": "RU",
    #"created_at": "2016-09-13T10:00:15Z",
    #"direction": 184,
    #"etag": "W/\"datetime'2022-10-03T00%3A37%3A33.8357302Z'\"",
    #"imei": "358679068009470",
    #"label": "Mercedz Benz",
    #"last_update": "2022-10-03T00:37:15Z",
    #"lat": 56.0036,
    #"lon": 37.18986
    #}
    #{'PartitionKey': 'customfield', 'RowKey': '50043', 'Timestamp': datetime.datetime(2022, 10, 2, 6, 1, 17, 429404, tzinfo=tzutc()), 'CustomField': '{"PackageType": null, "PackingListUpload": null, "TrackingLink": null}', 'etag': 'W/"datetime\'2022-10-02T06%3A01%3A17.4294046Z\'"'}
    required_payload = {
        "vehicle_reg" : asset_det["assetName"],
        "route" : asset_det["label"],
        "group" : asset_det["clientName"],
        "htm" : goods_det["htm"],
        "packing_list" : goods_det["packing_list"],
        "tracking_link" : cf_det["TrackingLink"],
        "alert_name" : json_data["alert_type"],
        "location" : json_data["location"],
        "geo_reference" : json_data["address"],
        "alert_comment" : json_data["msg"],
        "time" : json_data["time"]
    }
    logging.info(required_payload)
    #{'vehicle_reg': 'FM920 - Beacons testing', 'route': 'VectorGlobe Fe+', 'htm': 'HTm123123123123', 'packing_list': ['pl1231231', 'pl54134123', 'pl15123123', 'pl5123132123'], 'tracking_link': 'http://please.com', 'alert_name': 'speeding', 'location': '56.71888,25.20018', 'geo_reference': 'Lici, Krapes pag., Ogres nov., Latvija', 'alert_comment': 'Driving speed is 82 km/h (Manual speed limit: 80 km/h)'}

    req_subject = required_payload["vehicle_reg"] + " on route " + required_payload.get("group", "Not Available") + "/" + required_payload["route"] + " has triggered the " + required_payload["alert_name"] + " alert."

    req_message ="Subject: "+req_subject+"\n\n"
    req_message += "Hi Customer," + "\n"
    req_message += req_subject + "\n"
    req_message += "Alert triggered at location coordinate " + required_payload["location"] + " which is " + required_payload["geo_reference"] + " on " + required_payload["time"] + " and the reason was " + required_payload["alert_comment"] + "\n"
    req_message += "You can access the live location using the tracking link " + required_payload["tracking_link"] + "\n\n"
    req_message += "The additional details for this are " + "\n"
    req_message += "HTM Number :" + required_payload["htm"] + "\n"
    for item in required_payload["packing_list"]:
        req_message += item + "\n"
    send_mail(to_email="helpdesk@vectorglobe.com", message=req_message)
