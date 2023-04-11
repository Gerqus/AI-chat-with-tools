from bs4 import BeautifulSoup
import requests
from constants import OpenAIRoles

from send_query_to_open_ai import MessageRepresentation, send_messages_history_to_open_ai, count_message_tokens

def get_page_content_summary(page_url: str) -> str:
    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
    }
    response = session.get(page_url)
    if response.status_code == 200:
        page_source = response.text
        parsed_page = BeautifulSoup(page_source, 'html.parser')
        page_text = parsed_page.get_text()
        page_text = page_text.replace('\n', ' ')
        page_text = page_text.replace('\t', ' ')
        page_text = page_text.replace('\r', ' ')
        page_text = page_text.replace('  ', ' ')

        chat_model_used = 'gpt-3.5-turbo'

        tokens_of_page_text = count_message_tokens(page_text)
        while (tokens_of_page_text > 4097):
            page_text = page_text[:-1 * (tokens_of_page_text - 500)]
            tokens_of_page_text = count_message_tokens(page_text)

        messages = [
            MessageRepresentation(
                "Your role is to summarize the text. Text provided to you is web page source striped from html tags, so it's chaotic. The goal is to extract most useful information from it and present it to the user in an informative way.",
                OpenAIRoles.system,
            ),
            MessageRepresentation(
                page_text,
                OpenAIRoles.user,
            )
        ]

        summary = send_messages_history_to_open_ai(messages, chat_model_used)
        return summary
    else:
        return ''
