import logging
import os
import readline
import sys
from datetime import datetime
from typing import List

import weaviate
from googlesearch import SearchResult

from constants import AvailableActions, OpenAIRoles, chat_model_used, openai_system_message
from get_page_content_summary import get_page_content_summary
from get_permission_from_user import get_permission_from_user

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-OpanAI-Api-Key": os.environ["OPENAI_API_KEY"],
    }
)

from convert_query_results_to_chatbot_readable import \
    convert_query_results_to_chatbot_readable
from delete_data_from_database import delete_data_from_database
from get_data_from_database import get_data_from_database
from parse_for_potential_action import parse_for_potential_action
from save_data_to_database import save_data_to_database
from send_query_to_open_ai import (MessageRepresentation,
                                   add_message_to_history,
                                   send_messages_history_to_open_ai)
from search_google import search_google

#log file name with date and time
if not os.path.exists('chats'):
    os.mkdir('chats')
log_filename = 'chats/chat_{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
terminal_output = logging.StreamHandler(stream=sys.stdout)
file_output = logging.FileHandler(log_filename, mode='a')
logger = logging.getLogger("weaviate")
logger.setLevel(logging.DEBUG)
logger.addHandler(terminal_output)
logger.addHandler(file_output)
log_msg = logger.info

log_msg("Welcome to the chatbot with tools! Type 'exit' to quit.")

messages_history: List[MessageRepresentation] = []
message_to_chatbot = ''

log_msg("Using model: " + chat_model_used)
log_msg("Using database: Weaviate")
log_msg("Using tokenizer: openai")
log_msg("Using system message: " + openai_system_message)
log_msg("---------- STARTING CHAT ----------")

try:
    while True:
        if message_to_chatbot == '':
            message_to_chatbot = input("You: ")
            log_msg("--- me: " + message_to_chatbot)

            if message_to_chatbot.lower() == "exit":
                log_msg("\nGoodbye!")
                break

            message_to_chatbot = "[user] " + message_to_chatbot
        
        else:
            log_msg("--- script: " + message_to_chatbot)

        # Process the user_message with the AI
        add_message_to_history(message_to_chatbot, OpenAIRoles.user, messages_history)
        ai_response = send_messages_history_to_open_ai(messages_history, chat_model_used)

        if ai_response == '' or ai_response is None:
            log_msg("\t(empty response)")
            retry = get_permission_from_user("The AI did not respond. Do you want to try again?")
            if not retry:
                message_to_chatbot = ''
                continue

        log_msg(f"--- {chat_model_used}: " + ai_response)
        add_message_to_history(ai_response, OpenAIRoles.assistant, messages_history)

        # The AI decides on the action and generates a query
        try:
            action_descriptor = parse_for_potential_action(ai_response)
        except Exception:
            message_to_chatbot = f'[script] There was an error chosing the tool (wrong tool name?). Please try again.'
            continue

        if action_descriptor.action_name == AvailableActions.store:
            log_msg("[store] tool selected")
            if (action_descriptor.action_data is None):
                message_to_chatbot = f"[{AvailableActions.store.value}] Could not store empty data string."
            else:
                save_data_to_database(client, action_descriptor.action_data)
                message_to_chatbot = "[script] Data stored successfully."
            continue
        elif action_descriptor.action_name == AvailableActions.retrieve:
            log_msg("[retrieve] tool selected")
            if (action_descriptor.action_data is None):
                message_to_chatbot = f"[{AvailableActions.retrieve.value}] Could not search by empty string."
            else:
                query_results = get_data_from_database(client, action_descriptor.action_data)
                chat_bot_readable_results: str | None = convert_query_results_to_chatbot_readable(query_results)
                if chat_bot_readable_results is None:
                    message_to_chatbot = f"[{AvailableActions.retrieve.value}] Could not retrieve data."
                else:
                    message_to_chatbot = "[script] Data retrieved successfully. Query results are:" + chat_bot_readable_results
            continue
        elif action_descriptor.action_name == AvailableActions.delete:
            log_msg("[delete] tool selected")
            if (action_descriptor.action_data is None):
                message_to_chatbot = f"[{AvailableActions.delete.value}] Could not delete by empty string."
            else:
                query_results = delete_data_from_database(client, action_descriptor.action_data)
                message_to_chatbot = "[script] Data deleted successfully." 
            continue
        elif action_descriptor.action_name == AvailableActions.google:
            log_msg("[google] tool selected")
            if (action_descriptor.action_data is None):
                message_to_chatbot = f"[{AvailableActions.google.value}] Could not search by empty string."
            else:
                user_permission = get_permission_from_user(f"Do you want to search on google for '{action_descriptor.action_data}'?")
                if not user_permission:
                    message_to_chatbot = "[script] Search denied."
                    continue
                log_msg("Search approved")
                search_result: List[SearchResult] = search_google(action_descriptor.action_data)
                message_to_chatbot = f"[script] search successful. Results are:\n" + "\n".join(["- " + search_result.url + " -> " + search_result.description + ";" for search_result in search_result])
            continue
        elif action_descriptor.action_name == AvailableActions.open:
            log_msg("[open] tool selected")
            if (action_descriptor.action_data is None):
                message_to_chatbot = f"[{AvailableActions.open.value}] Could not open page under empty string url."
            else:
                user_permission = get_permission_from_user(f"Do you want to open '{action_descriptor.action_data}' for getting a summary of content?")
                if not user_permission:
                    message_to_chatbot = "[script] Page open denied."
                    continue
                log_msg("Page open approved")
                page_summary: str = get_page_content_summary(action_descriptor.action_data)
                if page_summary == "":
                    message_to_chatbot = f"[{AvailableActions.open.value}] Could not open page under url {action_descriptor.action_data}. Sorry."
                message_to_chatbot = f"[script] open successful. Page summary: {page_summary}."
            continue
        else:
            message_to_chatbot = ''
            continue

        raise Exception("Unknown action detected or some action did not continue the loop")
except KeyboardInterrupt:
    log_msg("\nGoodbye!")
