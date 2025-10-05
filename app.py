from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.cosmos import CosmosClient
from typing import Dict, Any

from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

EMBEDDING_MODEL_ENDPOINT = os.getenv("EMBEDDING_MODEL_ENDPOINT")
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
subscription_key = os.getenv("subscription_key")

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
            c.genre,
            c.rating,
            c.release_year,
            c.plot_summary,
            c.plot_synopsis,
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
    

# def get_average_rating():
#     db_query = """
#         SELECT VALUE AVG(StringToNumber(c.rating))
#         FROM c
#         WHERE IS_DEFINED(c.rating) AND IS_STRING(c.rating) AND NOT IS_NULL(c.rating)
#     """
#     results = container.query_items(
#         query=db_query,
#         enable_cross_partition_query=True
#     )
#     try:
#         average_rating = next(results) 
#         return average_rating if average_rating is not None else 0.0
#     except StopIteration:
#         return 0.0

    
def get_embedding(container, movie_name: str):
    find_movie_query = """
        SELECT VALUE c.embedding 
        FROM c
        WHERE c.title = @movie_name
    """
    parameters = [ 
        {"name": "@movie_name", "value": movie_name}
    ]

    try:
        result_items = list(container.query_items(
            query=find_movie_query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        if result_items:
            return result_items[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching embedding for movie '{movie_name}': {e}")
        return None


def find_similar(movie_name: str , top_k=5):
    query_embedding = get_embedding(container,movie_name)
    if query_embedding is None:
        print(f"Error: Could not find embedding for source movie '{movie_name}'.")
        return []
    
    db_query = """
        SELECT TOP @num_results
            c.title,
            c.genre,
            c.rating,
            c.release_year,
            c.plot_summary,
            c.plot_synopsis,
            VectorDistance(c.embedding, @embedding) AS similarity_score
        FROM c
        ORDER BY VectorDistance(c.embedding, @embedding)
    """
    parameters =[
        {"name": "@embedding", "value": query_embedding},
        {"name": "@num_results", "value": top_k + 1}
    ]

    try:
        results = list(container.query_items(
            query=db_query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        filtered_results = [
            result for result in results 
            if result['title'] != movie_name
        ]

        return filtered_results[:top_k]
        
    except Exception as e:
        print(f"Error in finding similar movies: {e}")
        return []


query = "Find action movies with sad ending"
results = vector_search(query,top_k=3)
for idx, item in enumerate(results):
    print(item)

movie = "Wet Hot American Summer"

results1 = find_similar(movie,5)
print (results1)