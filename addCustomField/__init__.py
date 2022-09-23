import logging
import requests
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )


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
