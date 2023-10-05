from langchain.tools import BaseTool
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import streamlit as st
import openai
from dotenv import dotenv_values

### parameters #########
config = dotenv_values('conf.env')
openai.api_key = config['OPENAI_API_KEY']
SECURE_CONNECT_BUNDLE_PATH = config['SECURE_CONNECT_BUNDLE_PATH']
ASTRA_CLIENT_ID = config['ASTRA_CLIENT_ID']
ASTRA_CLIENT_SECRET = config['ASTRA_CLIENT_SECRET']
cloud_config = {
    'secure_connect_bundle': SECURE_CONNECT_BUNDLE_PATH
    }
auth_provider = PlainTextAuthProvider(ASTRA_CLIENT_ID, ASTRA_CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()
 

class Waiter(BaseTool):
    name = "Waiter"
    description = "Use this tool as you are waiter and help customers with their order. You need to check what is available in the menu but you can provide concise responses.You also tell the total cost of their order. "

    def _run(self,user_question):
        KEYSPACE_NAME = 'vector'
        TABLE_NAME = 'restaurant'
        model_id = "text-embedding-ada-002"
        embedding = openai.Embedding.create(openai_api_key=openai.api_key,input=user_question, model=model_id)['data'][0]['embedding']
        for row in session.execute(f"SELECT document_id,document,embedding_vector FROM {KEYSPACE_NAME}.{TABLE_NAME} ORDER BY embedding_vector ANN OF {embedding} LIMIT 1"):
                res = row.document 

        return res 

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")


class TotalAmount(BaseTool):
    name = "TotalAmount"
    description = "Use this tool as you are waiter and You can provide concise responses. You don't need to tell each price of the food but you can tell the total cost of the order"
    
    def _run(self,user_question):
        KEYSPACE_NAME = 'vector'
        TABLE_NAME = 'restaurant'
        model_id = "text-embedding-ada-002"
        embedding = openai.Embedding.create(openai_api_key=openai.api_key,input=user_question, model=model_id)['data'][0]['embedding']
        for row in session.execute(f"SELECT document_id,document,embedding_vector FROM {KEYSPACE_NAME}.{TABLE_NAME} ORDER BY embedding_vector ANN OF {embedding} LIMIT 1"):
                res = row.document 

        return res 

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")