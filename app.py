from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.cosmos import CosmosClient
from typing import Dict, Any

from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

subscription_key = os.getenv("subscription_key")
EMBEDDING_MODEL_ENDPOINT = os.getenv("EMBEDDING_MODEL_ENDPOINT")
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")

cosmos_client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

embedding_model = AzureOpenAIEmbeddings(
    azure_endpoint=EMBEDDING_MODEL_ENDPOINT,
    api_key=subscription_key,
)

def vector_search(query_text,top_k=5):
    try:
        query_embedding = embedding_model.embed_query(query_text)
    except Exception as e:
        print("Error in embedding")


    db_query = """
        SELECT TOP @top_k
            c.title,
            c.genres,
            c.rating,
            VectorDistance(c.embedding, @query_embedding) AS similarity_score
        FROM c
        ORDER BY VectorDistance(c.embedding, @query_embedding)
        """
    parameters = [ 
        {"name": "@query_embedding", "value": query_embedding},
        {"name": "@top_k", "value": top_k}
    ]

    try:
        results = list(container.query_items(
            query=db_query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        return results
    
    except Exception as e:
        print("Error in vector search: {e} could not find vector")
        return []
    

def get_average_rating():
    db_query = """
        SELECT VALUE AVG(StringToNumber(c.rating))
        FROM c
        WHERE IS_DEFINED(c.rating) AND IS_STRING(c.rating) AND NOT IS_NULL(c.rating)
    """
    results = container.query_items(
        query=db_query,
        enable_cross_partition_query=True
    )
    try:
        average_rating = next(results) 
        return average_rating if average_rating is not None else 0.0
    except StopIteration:
        return 0.0
    
query = "Find action movies with sad ending"
results = vector_search(query,top_k=3)
for idx, item in enumerate(results):
    print(item)

print(f"Average rating of all movies: {get_average_rating()}")