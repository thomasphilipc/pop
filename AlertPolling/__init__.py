import datetime
import logging
from re import A
import requests
import json
import azure.functions as func
from datetime import timedelta
import os


def alert_types(item):
    # use logic to filter the alerts that should be monitored
    if item.get("alert_type") in ["in_object","not_in_obj"]:
        return True
    else:
        return False

def get_units(json_list):
    unit_lists=[]
    for item in json_list:
        units=item.get("units",None)
        unit_in_group=units.strip("[']").replace("'","").split(', ')
        for item in unit_in_group:
            unit_lists.append(item)
    return (unit_lists)


def main(mytimer: func.TimerRequest, clientTable, msg : func.Out[str]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    payload = json.loads(json.loads(json.dumps(clientTable)))

    logging.info(payload)
    #'[{"apiKey":"dasdsd4234","clientKey":"testkey4","clientName":"VectorGlobe Fe+","customField":"{\'Package Type\': {\'id\': 2544281, \'settings\': {\'options\': {\'6338f5d755f12\': \'type1\', \'6338f5d755f15\': \'type 2\', \'6338f5d755f16\': \'type 3\'}}}, \'Packing List Upload\': {\'id\': 2526197, \'settings\': []}, \'Tracking Link\': {\'id\': 2541055, \'settings\': []}}","enabled":true,"process_alerts":true,"total_units":"14","PartitionKey":"1209","RowKey":"58234"},{"apiKey":"511687b33edad08b83303995472b3106ec3dff13","clientKey":"testkey3","clientName":"SteadyRoutes","customField":"{\'Trailer Type\': {\'id\': 1492749, \'settings\': []}, \'Device ID\': {\'id\': 2353966, \'settings\': []}, \'Trailer Plate Number\': {\'id\': 2013009, \'settings\': []}, \'Trailer Reg Expiry\': {\'id\': 2013010, \'settings\': []}}","enabled":true,"process_alerts":false,"total_units":"34","PartitionKey":"24752","RowKey":"58572"},{"apiKey":"30484e21fef6179c8bfce893968c4fcd2ce29cc4","clientKey":"testkey2","clientName":"Huawei","customField":"{\'Vehicle Inspection Date\': {\'id\': 2404102, \'settings\': []}, \'Shipment ID\': {\'id\': 2323261, \'settings\': []}, \'Driver Name\': {\'id\': 2323262, \'settings\': []}, \'Driver Phone No.\': {\'id\': 2323263, \'settings\': []}, \'Carrier Name\': {\'id\': 2323264, \'settings\': []}, \'Business Type\': {\'id\': 2323265, \'settings\': {\'options\': {\'628dbbf3d88d2\': \'1: Hong Kong local Pickup\', \'628dbbf3d88d6\': \'2: China-Hong Kong transportation\', \'628dbbf3d88d7\': \'3: Revolving transportation of sorting centre\', \'628dbbf3d88d8\': \'4: Transportation in China\', \'630dab7541ab6\': \'8: DSC OUTBOUND\'}}}, \'Vehicle Style\': {\'id\': 2323266, \'settings\': {\'options\': {\'628dbbf3d8c53\': \'VS1: common rail truck\', \'628dbbf3d8c56\': \'VS2: common van\', \'628dbbf3d8c57\': \'VS3: container tractor\', \'628dbbf3d8c58\': \'VS4: flat truck\', \'628dbbf3d8c59\': \'VS5: closed truck\', \'628dbbf3d8c5a\': \'VS6: tank truck\', \'628dbbf3d8c5b\': \'VS7: Special structure truck\', \'628dbbf3d8c5d\': \'VS8: other types\', \'628dbbf3d8c5e\': \'VS9: tractor\', \'628dbbf3d8c5f\': \'VS10: semi-trailer-car cabinet\', \'628dbbf3d8c60\': \'VS11: semi-trailer-plate\', \'628dbbf3d8c61\': \'VS12: Semi-trailer-container\'}}}, \'Truck Registration Date\': {\'id\': 2323267, \'settings\': []}, \'Truck Registration Expiry\': {\'id\': 2323268, \'settings\': []}, \'LSP Code\': {\'id\': 2323269, \'settings\': []}, \'Vehicle Type\': {\'id\': 2323270, \'settings\': []}, \'Car Company\': {\'id\': 2323271, \'settings\': []}, \'Car Country Name\': {\'id\': 2323272, \'settings\': []}, \'Car Manager Name\': {\'id\': 2323273, \'settings\': []}, \'Car Manager Phone. No.\': {\'id\': 2323274, \'settings\': []}, \'License Plate (Other Aux)\': {\'id\': 2323275, \'settings\': []}, \'Bill ID\': {\'id\': 2323277, \'settings\': []}, \'Bill Type\': {\'id\': 2323278, \'settings\': []}}","enabled":true,"process_alerts":false,"total_units":"2","PartitionKey":"40466","RowKey":"60317"}]'

    # the time to check back upto is given as config
    pollduration = int(os.environ["pollduration"])
    #details from payload

    units=get_units(payload)

    for item in payload:
        if item["process_alerts"]:
            group_id= item['RowKey']
            apikey=item['apiKey']
    
            #times
            end = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat().split('.')[0]+'Z'
            start = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)-timedelta(minutes=pollduration)).isoformat().split('.')[0]+'Z'

            endpoint = "https://mapon.com/"
            path = "api/v1/alert/list.json?key="+apikey
            params="&from="+start+"&till="+end+"&include[]=address&include[]=location&limit=150&page=1"
            constructed_url = endpoint + path + params

            payload={}
            headers = {}



            response = requests.request("GET", constructed_url, headers=headers, data=payload)

            alerts_json=response.json()

            alert_list=alerts_json["data"]
            
            for item in alert_list:
                
                if (str(item.get("unit_id")) in units) and alert_types(item):
                    msg.set(json.dumps(item))


    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
