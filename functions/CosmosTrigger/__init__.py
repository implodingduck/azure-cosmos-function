import logging

import azure.functions as func
from azure.cosmos import exceptions, CosmosClient, PartitionKey
from datetime import datetime

import os 
import random
import uuid

def main(documents: func.DocumentList) -> str:
    if documents:
        logging.info(f'Number of Documents: {len(documents)}')
        logging.info('Document id: %s', documents[0]['id'])
    client = CosmosClient(os.environ.get('COSMOSDB_ENDPOINT'), os.environ.get('COSMOSDB_KEY'))
    db = client.get_database_client(os.environ.get('COSMOSDB_NAME'))
    container = db.get_container_client(os.environ.get('COSMOSDB_CONTAINER'))
    for doc in documents:
        logging.info(f'Before: {doc}')
        doc['product'] = int(doc['multiplier']) * int(doc['multiplicand'])
        now = datetime.now()
        doc['updatedDate'] = now.strftime("%m/%d/%Y %H:%M:%S")
        logging.info(f'After: {doc}')
        container.upsert_item(body=doc)
        logging.info('Upsert Done!')