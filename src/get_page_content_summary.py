import re
import openai
import requests
from src.constants import OpenAIRoles
from newspaper import Article

from src.send_query_to_open_ai import MessageRepresentation

parts_splitter = '=== !!! ==='

system_message = MessageRepresentation(
    f"""Your role is to extract key insights from the text. Your response limit is set to 1000 tokens - mind it.
Text will consist of three parts: title, insights from previous processing up to this point and current text batch to summarize.
Each part will be separated by the following string: {parts_splitter}
The goal is to extract most useful information from whole text and. Be technical, as if you would list the most important points of the text.
Be absolutelly sure to take into account insights from previous processing and DO NOT ABANDON them. Integrate them. You can use them to make your summary more complete.""",
    OpenAIRoles.system,
)

chat_model_used = 'gpt-3.5-turbo'

def get_page_content_summary(page_url: str) -> str:
    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
    }
    response = session.get(page_url)
    if response.status_code == 200:
        page_source = response.text
        article = Article(page_url)
        article.set_html(page_source)
        article.parse()
        page_title = article.title
        page_text = article.text
        page_text = page_text.replace('\n', ' ')
        page_text = page_text.replace('\t', ' ')
        page_text = page_text.replace('\r', ' ')
        page_text = page_text.replace('  ', ' ')

        text_batches = ['']
        for page_sentences in re.split(r'\s', page_text):
            current_batch_index = len(text_batches) - 1
            if len(text_batches[current_batch_index]) + len(page_sentences) + 1 < 3000:
                text_batches[current_batch_index] += " " + page_sentences
            else:
                text_batches.append(page_sentences)

        print("Created total of: " + str(len(text_batches)) + " batches of text to summarize.")
        for i, batch in enumerate(text_batches):
            print(f"Batch #{i} length: {len(batch)}")


        summary = '<no summary has been made yet>'
        for i, batch in enumerate(text_batches):
            print("Summarizing batch no. " + str(i + 1) + " of " + str(len(text_batches)) + " (batch len: " + str(len(batch)) + ")")

            messages = [
                system_message.to_msg(),
                MessageRepresentation(
                    parts_splitter.join([page_title, summary, batch]),
                    OpenAIRoles.user,
                ).to_msg()
            ]

            completion = openai.ChatCompletion.create(
                model=chat_model_used,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
                messages=messages
            )

            summary = completion.choices[0].message.content # type: ignore
            print("Summary received: " + summary)

        return summary
    else:
        return ''
