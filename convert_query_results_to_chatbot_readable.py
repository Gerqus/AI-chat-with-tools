from typing import List
from constants import database_dataset_text_field_name
from get_data_from_database import SearchResult, SearchResultEntry

def convert_query_results_to_chatbot_readable(result: SearchResult) -> str:
    formatted_result = 'Results, ordered from most to least similar:\n'
    print(result)
    memories: List[SearchResultEntry] = result['Memories']
    memories.sort(key=lambda x: x["_additional"]["distance"])
    formatted_result += "\n".join(["- " + hit[database_dataset_text_field_name] + ";" for hit in memories])
    return formatted_result
