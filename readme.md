# Chat with tools

This is simple python program that uses external chat GPT and instructs it on using some tools. Thanks to it's "understanding" of tools effects and potential benefits we don't have to teach GPT on when to use what.

Notice - as of now (11.04.2023) only GPT-4 handles this correctly. GPT-3.5 tries to mimic the tools and provides own results of tools usage. checked for memory store/retrieve tools.

## Requirements

This tool uses [Weaviate](https://weaviate.io/) as vector database and assumes you will host own [docker image](https://weaviate.io/developers/weaviate/installation/docker-compose) of it.

Please remember to add to your docker image

```yaml
DEFAULT_VECTORIZER_MODULE: text2vec-openai
ENABLE_MODULES: text2vec-openai
```

or other definition of txt2vec tool

## Setup

After installing all requirements and setting up docker with Weaviate, just run `setup.py` file to create data structures in vector database.

## Usage

Run `main.py` file. It will log what is going on and what it does. Your input is expected on "You: " prompt. Sometimes, when AI decides to use some tool, script will not wait for your imput, but will just execute tool script assigned to it and talk back to conversational AI either with execution result data or with a report of an error.

Whole conversation will be printed to you in terminal and wrote into a chat file with timestamp in its name. Both outputs contain the very same content.
