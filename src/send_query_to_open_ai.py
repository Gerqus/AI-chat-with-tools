from dataclasses import dataclass
from typing import List
import openai
import torch
from src.constants import OpenAIRoles
from transformers import AutoTokenizer
from src.constants import openai_system_message

tokenizer = AutoTokenizer.from_pretrained("gpt2")

system_message = {
    "role": "system",
    "content": openai_system_message,
}

TIMEOUT_SECS = 60
MESSAGES_COUNT_LIMIT = 4000

@dataclass
class MessageRepresentation:
    content: str
    role: OpenAIRoles
    tokens_count: int

    def __init__(self, content: str, role: OpenAIRoles, tokens_count: int = 0):
        self.content = content
        self.role = role
        if tokens_count == 0:
            self.tokens_count = count_message_tokens(content)
        self.tokens_count = tokens_count
    
    def to_msg(self):
        return {
            "role": self.role.name,
            "content": self.content
        }

def count_message_tokens(message: str) -> int:
    input_ids = torch.tensor(tokenizer.encode(message)).unsqueeze(0)
    num_tokens = input_ids.shape[1]
    return num_tokens

total_history_tokens_count = count_message_tokens(system_message["content"])

def add_message_to_history(message: str, role: OpenAIRoles, messages_history: List[MessageRepresentation]):
    global total_history_tokens_count

    message_tokens_count = count_message_tokens(message)

    messages_history.append(MessageRepresentation(
        content = message,
        role = role,
        tokens_count = message_tokens_count
    ))
    total_history_tokens_count += message_tokens_count

def send_messages_history_to_open_ai(messages_history: List[MessageRepresentation], model) -> str:
    global total_history_tokens_count

    while True:
        if total_history_tokens_count > MESSAGES_COUNT_LIMIT:
            # pop both chatbot and user messages
            total_history_tokens_count -= messages_history[0].tokens_count
            messages_history.pop(0)
            if len(messages_history) > 0:
                total_history_tokens_count -= messages_history[0].tokens_count
                messages_history.pop(0)
        else:
            break

        if len(messages_history) == 0:
            raise Exception("Error: Could not create chat completion. Messages history is empty.")
    
    messages = [system_message]
    for message_from_history in messages_history:
        messages.append({
            "role": message_from_history.role.name,
            "content": message_from_history.content
        })
    
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            max_tokens=100,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            timeout=TIMEOUT_SECS,
            messages=messages
        )

        return completion.choices[0].message.content # type: ignore

    except Exception as e:
        global retries_count
        print(e)
        print("Error: Could not create chat completion.")
        return ""
