import logging

import azure.functions as func
from azure.cosmos import exceptions, CosmosClient, PartitionKey
from datetime import datetime

import os 
import random
import uuid

def main(req: func.HttpRequest) -> func.HttpResponse:
    trigger_name = 'InsertRows'
    logging.info(f'{trigger_name} HTTP trigger function processed a request.')
    client = CosmosClient(os.environ.get('COSMOSDB_ENDPOINT'), os.environ.get('COSMOSDB_KEY'))
    db = client.get_database_client(os.environ.get('COSMOSDB_NAME'))
    container = db.get_container_client(os.environ.get('COSMOSDB_CONTAINER'))
    req_body = req.get_json()
    logging.info(req_body)
    num_inserts = 1
    if 'num' in req_body:
        num_inserts = int(req_body['num'])

    for i in range(num_inserts):
        now = datetime.now()
        new_item = {
            'id': str(uuid.uuid4()),
            'multiplier': random.randint(1,100),
            'multiplicand': random.randint(1,100),
            'product': 0,
            'sum': 0,
            'createdDate': now.strftime("%m/%d/%Y %H:%M:%S"),
            'updatedDate': now.strftime("%m/%d/%Y %H:%M:%S")
        }
        container.create_item(body=new_item)
    return func.HttpResponse(
        f'{trigger_name}HttpTrigger called... {num_inserts} added',
        status_code=201
    )

