from weaviate import Client
from constants import database_collection_name, database_dataset_text_field_name

def save_data_to_database(client: Client, text_to_save: str):
    client.data_object.create(
        class_name=database_collection_name,
        data_object={database_dataset_text_field_name: text_to_save},
    )
