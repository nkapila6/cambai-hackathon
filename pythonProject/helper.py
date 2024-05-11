import gradio as gr
import requests
import json

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    StringPromptTemplate,
    FewShotPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

import time

import mishkal.tashkeel


_ = load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
camb_ai_key = os.getenv("CAMB_AI_KEY")

language_dict = {"en": 1, "ar": 4}


def get_task_id(input_str: str, language: int = 1):
    print(f"Language selected: {language}")
    url = "https://client.camb.ai/apis/tts"
    payload = {
        "text": input_str,
        "voice_id": 8745,
        "language": language,
        "gender": 0,
        "age": 123,
    }
    headers = {"x-api-key": camb_ai_key, "Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)

    return eval(response.text)


# Get poll status
def get_poll_status(task_id: str):
    # Job Status
    url = f"https://client.camb.ai/apis/tts/{task_id}"

    headers = {"x-api-key": camb_ai_key}

    response = requests.request("GET", url, headers=headers)

    return response.text


def clean_input(raw_input: str):
    openai_model = ChatOpenAI(
        temperature=0, api_key=openai_api_key, model="gpt-3.5-turbo"
    )
    SYSTEM_PROMPT = """You are an advanced language model trained to rephrase sentences while removing inappropriate, offensive, or explicit content. Your task is to take any input sentence, no matter how vulgar or offensive, and rewrite it in a polite, family-friendly manner without losing the core meaning."""
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", human)]
    )

    chain = prompt | openai_model | StrOutputParser()
    paraphrased_sentence = chain.invoke({"text": raw_input})
    return paraphrased_sentence


def cambAI_TTS(input_str: str, language: str):
    print(f"Input text: {input_str}")
    if language == "en":
        paraphrased_sentence = clean_input(input_str)
    elif language == "ar":
        vocalizer = mishkal.tashkeel.TashkeelClass()
        paraphrased_sentence = vocalizer.tashkeel(input_str)

    print(f"Paraphrased text: {paraphrased_sentence}")
    task_id = get_task_id(paraphrased_sentence, language=language_dict[language])[
        "task_id"
    ]
    if language == "en":
        time.sleep(10)
    elif language == "ar":
        time.sleep(40)
    poll_status = get_poll_status(task_id)
    poll_status = eval(poll_status)
    print(poll_status)
    if poll_status["status"] == "SUCCESS":
        tts_result = requests.get(
            f"https://client.camb.ai/apis/tts_result/{poll_status['run_id']}",
            headers={"x-api-key": camb_ai_key},
            stream=True,
        )
        with open(f"saved_stream_{language}.wav", "wb") as f:
            for chunk in tts_result.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Audio saved as saved_stream_{language}.wav")

    if poll_status["status"] == "FAILED":
        print("Job failed!")
        return None

    return f"saved_stream_{language}.wav", paraphrased_sentence


if __name__ == "__main__":
    # cambAI_TTS("You are a horrible and nasty person!", "en")
    cambAI_TTS("أنا أتعلم اللغة العربية بشكل جيد.", "ar")
