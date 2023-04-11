import weaviate
from src.constants import database_collection_name, database_dataset_text_field_name

# Connect to database server
client = weaviate.Client("http://localhost:8080")

# Create the Weaviate schema
schema = {
    "classes": [
        {
            "class": database_collection_name,
            "description": "A vector object",
            "properties": [
                {
                    "name": database_dataset_text_field_name,
                    "description": "Single memory",
                    "dataType": ["string"],
                    "moduleConfig": {
                        "text2vec-openai": {
                            "vectorizePropertyName": False,
                        }
                    },
                }
            ],
            "vectorIndexConfig": {"distance": "cosine"},
            "moduleConfig": {
                "text2vec-openai": {
                    "vectorizeClassName": False
                }
            }
        }
    ]
}
client.schema.delete_all()
client.schema.create(schema)
