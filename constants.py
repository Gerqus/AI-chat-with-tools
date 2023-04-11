from enum import Enum

database_collection_name = "Memories"
database_dataset_text_field_name = "memory"

class AvailableActions(Enum):
    store = "store"
    retrieve = "retrieve"
    delete = "delete"

class OpenAIRoles(Enum):
    user = "user",
    system = "system",
    assistant = "assistant",

openai_system_message = """As ChatGPT, you now have additional tools to enhance your assistance. To use a tool, write "[<toolname>]" before your message, which will be entirely processed by the designated tool. The tool will respond using the same format: "[script] result of tool action". Messages prefixed with "[script]" do not come from the user. Always consider the available tools when responding to user requests and utilize them if they can improve your performance as ChatGPT. Before concluding that you cannot fulfil a request, try to find a suitable tool to help you achieve the desired outcome. When you choose to send a message directly to the user without using a tool, refrain from using any prefix. Never pretend to use tools and never generate response that tol would provide, isntead just use the tool. Strictly obey the messages format. This is because prefixes are reserved for directing messages to specific tools. Users will not be able to see messages sent to or received from tools, as these interactions remain discreet. If you want to use the tool and aswer to user, first use tool with properly formatted query, tool will respond, then you san use that response and user question to answear to user. The list of available tools is as follows:"""

tools = {
    AvailableActions.retrieve: """enables you to retrieve data from your long-term memory that was previously stored using the 'store' tool. Be aware that you may not recall storing the data previously. Searches are based on query string similarity. The top 1, 2 or 3 most similar memories will be returned""",
    AvailableActions.store: """enables you to save data in your long-term memory, which can later be accessed using the 'retrieve' tool. Pair of store-retrieve tools works like this: when you write out: "[store] Anna likes to eat apples" This stores whole "Anna likes to eat apples" inside the memory, because this whole text was prefixed with [store] command. You will be send a response like this: "[script] Data stored in database""",
    AvailableActions.delete: """enables you to delete previous saved data from your long-term memory. Forgetting can be useful for dropping less relevant memories and increasing search results relevant"""
    # "google": "allows you to search the internet using google search engine",
    # "open": "allows you to fetch summed up contents of a web page",
}

chat_model_used = "gpt-4"
