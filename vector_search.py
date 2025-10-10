from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.cosmos import CosmosClient
from typing import Dict, Any, Tuple, Optional, List

from dotenv import load_dotenv
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
            c.id,
            c.title,
            c.genres,
            c.rating,
            c.year,
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


#find similar movies based on input

def find_similar(movie_name: str, top_k=5 ,year_range = [1921,2025], rating_range = [0.0,10.0], genre = None):
    query_embedding = get_embedding(container,movie_name)
    if query_embedding is None:
        print(f"Error: Could not find embedding for source movie '{movie_name}'.")
        return []
    
    if genre == None:
        genre = []

    filters = get_filters(year_range,rating_range,genre)

    if filters:
        db_query = f"""
        SELECT TOP @num_results
            c.id,
            c.title,
            c.genres,
            c.rating,
            c.year,
            c.plot_summary,
            c.plot_synopsis,
            VectorDistance(c.embedding, @embedding) AS similarity_score
        FROM c
        WHERE {filters}
        ORDER BY VectorDistance(c.embedding, @embedding)
    """
    else:
        db_query = f"""
        SELECT TOP @num_results
            c.id,
            c.title,
            c.genres,
            c.rating,
            c.year,
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


# converts Range of filters to a String query

def get_filters(year_range: Tuple[int,int], rating_range: Tuple[float,float], genres_list: List[str]) -> str:
    conditions = []
    conditions.append(f"c.year >= {year_range[0]}  AND c.year <= {year_range[1]}")
    conditions.append(f"c.rating >= {rating_range[0]} AND c.rating <= {rating_range[1]}")
    
    if genres_list:
        genre_filter = []
        for genres in genres_list:
            escaped_genre = genres.replace("'", "''")
            genre_filter.append(f"ARRAY_CONTAINS(c.genres, '{escaped_genre})")
        if genre_filter:
            conditions.append(f"({' OR '.join(genre_filter)})")
    return " AND ".join(conditions) if conditions else ""


# search function with filters

def search_with_filtersAndPrompt(query_text:str, top_k=5 ,year_range = [1921,2025], rating_range = [0.0,10.0], genre = None):
    if genre == None:
        genre = []
    
    query_embedding = embedding_model.embed_query(query_text)
    filters = get_filters(year_range,rating_range,genre)

    if filters:
        db_query = f"""
            SELECT TOP @num_results
                c.id,
                c.title,
                c.genres,
                c.rating,
                c.year,
                c.plot_summary,
                c.plot_synopsis,
                VectorDistance(c.embedding, @embedding) AS similarity_score
            FROM c
            WHERE {filters}
            ORDER BY VectorDistance(c.embedding, @embedding)
        """
    else:
        db_query = f"""
            SELECT TOP @num_results
                c.id,
                c.title,
                c.genres,
                c.rating,
                c.year,
                c.plot_summary,
                c.plot_synopsis,
                VectorDistance(c.embedding, @embedding) AS similarity_score
            FROM c
            ORDER BY VectorDistance(c.embedding, @embedding)
        """
    parameters = [
        {"name": "@embedding", "value": query_embedding},
        {"name": "@num_results", "value": top_k}
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

    
    




# movie = "Wet Hot American Summer"

# results1 = find_similar(movie,2)
# print (results1)