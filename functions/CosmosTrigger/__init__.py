import logging

import azure.functions as func
from azure.cosmos import exceptions, CosmosClient, PartitionKey
from datetime import datetime

import os 
import random
import uuid
import json

def main(documents: func.DocumentList) -> str:
    if documents:
        logging.info(f'Number of Documents: {len(documents)}')
        logging.info('Document id: %s', documents[0]['id'])
    client = CosmosClient(os.environ.get('COSMOSDB_ENDPOINT'), os.environ.get('COSMOSDB_KEY'))
    db = client.get_database_client(os.environ.get('COSMOSDB_NAME'))
    container = db.get_container_client(os.environ.get('COSMOSDB_CONTAINER'))
    for doc in documents:
        doc_json = json.loads(doc.to_json())
        logging.info(f'Before: {doc_json}')
        if doc_json['product'] == 0:
            doc_json['product'] = int(doc_json['multiplier']) * int(doc_json['multiplicand'])
            now = datetime.now()
            doc_json['updatedDate'] = now.strftime("%m/%d/%Y %H:%M:%S")
            logging.info(f'After: {doc_json}')
            container.upsert_item(body=doc_json)
            logging.info('Upsert Done!')