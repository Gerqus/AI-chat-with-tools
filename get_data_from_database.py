from dataclasses import dataclass
from typing import List
from weaviate import Client
from constants import database_collection_name, database_dataset_text_field_name

@dataclass
class AdditionalInformation(dict):
    distance: float
    id: str

@dataclass
class SearchResultEntry(dict):
    _aditional: AdditionalInformation
    memory: str
    
@dataclass
class SearchResult(dict):
    # Memories is value of database_collection_name
    Memories: List[SearchResultEntry]

def get_data_from_database(client: Client, search_query: str) -> SearchResult:
    search_params = {
        "concepts": [search_query]
    }
    response = (
        client.query
            .get(database_collection_name, properties=[database_dataset_text_field_name])
            .with_additional(["distance", "id"])
            .with_near_text(search_params)
            .with_limit(3)
            .do()
    )
    return response["data"]["Get"]
