from weaviate import Client
from src.constants import database_collection_name
from src.get_data_from_database import get_data_from_database

def delete_data_from_database(client: Client, text_to_delete: str):
    search_result = get_data_from_database(client, text_to_delete)
    if search_result is not None:
        entry_id = search_result[database_collection_name][0]["_additional"]["id"]
        client.data_object.delete(
            class_name=database_collection_name,
            uuid=entry_id,
        )
