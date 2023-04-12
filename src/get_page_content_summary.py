import re
from typing import List
from bs4 import BeautifulSoup
from datasets import Dataset
import requests
import torch
from transformers import pipeline, AutoTokenizer
from src.constants import summarization_batch_size

device = "cuda:0" if torch.cuda.is_available() else "cpu"
device_map = {
    "": device,
}
summarize = pipeline(task="summarization", model="facebook/bart-large-cnn", device_map=device_map)
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

chat_model_used = 'gpt-3.5-turbo'

def generate_ngrams(list_of_words: List[str], n: int, shift: int) -> List[str]:
    ngrams = []
    if n >= len(list_of_words):
        return [' '.join(list_of_words)]
    i = 0
    for i in range(0, len(list_of_words) - n + 1, shift):
        ngrams.append(' '.join(list_of_words[i:i+n]))
    i += shift
    ngrams.append(' '.join(list_of_words[i:i+n]))
    return ngrams

def summarize_text(batch):
    inputs = tokenizer(batch["summary_text"], return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}  # Move the inputs to the GPU
    summaries = summarize.model.generate(**inputs)
    summary_texts = [tokenizer.decode(summary, skip_special_tokens=True) for summary in summaries]
    return {"summary_text": summary_texts}

def get_page_content_summary(page_url: str) -> str:
    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
    }
    response = session.get(page_url)
    if response.status_code == 200:
        page_source = response.text
        parsed = BeautifulSoup(page_source, 'html.parser')
        page_title = parsed.title
        page_text = parsed.text
        page_text = page_text.replace('\n', ' ')
        page_text = page_text.replace('\t', ' ')
        page_text = page_text.replace('\r', ' ')
        page_text = page_text.replace('  ', ' ')

        extracted_code_blocks = []
        for code_block in parsed.find_all('code'):
            extracted_code_blocks.append(code_block.text)
        summaries: List[str] = [f"{page_title}: {sentence}" for sentence in re.split(r'(\w+?)\.', page_text) if len(sentence) > 0]
        while len(summaries) > 1:
            ngrams = generate_ngrams(summaries, 25, 5)
            summaries_dataset = Dataset.from_dict({'summary_text': ngrams})
            new_summaries_dataset = summaries_dataset.map(summarize_text, batched=True, batch_size=summarization_batch_size)
            summaries = new_summaries_dataset["summary_text"]
        return summaries[0]
    else:
        return ''
