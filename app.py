import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from typing import Callable
from dotenv import load_dotenv
load_dotenv()

class Limoncito:
    # Define all credentials
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    openai.api_key = os.environ.get("OPENAI_API_KEY") 

    # Define the OpenAI Davinci model
    COMPLETIONS_MODEL = "text-davinci-002"
    COMPLETIONS_API_PARAMS = {
        "temperature": 0.0,
        "max_tokens": 300,
        "model": COMPLETIONS_MODEL,
    }
    app = App(token=SLACK_BOT_TOKEN)

    def __init__(self):
        pass

    @staticmethod
    def get_answer(message: str) -> str:
        # creating a proper prompt for the API
        message = f"You are a ChatBot, that would answer Crypto questions. If you don't know the answer, please, response only with a 'I don't know that'. Q: {message}\nA:"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=message,
            temperature=0.5,
            max_tokens=300,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response["choices"][0]["text"].strip(" \n")

@Limoncito.app.event("app_mention")
def mention_handler(body: dict, say: Callable):
    sender_id = f"<@{body.get('event', {}).get('user')}>"
    bot_id = body.get("event", {}).get("text").split()[0]
    message = body.get("event", {}).get("text")
    message = message.replace(bot_id, "").strip()
    if message:
        answer = Limoncito.get_answer(message)  
        say(f"Hey {sender_id}: {answer}")
    else:
        say(f"Hey! Please send a message to me")

if __name__ == "__main__":
    handler = SocketModeHandler(Limoncito.app, Limoncito.SLACK_APP_TOKEN)
    handler.start()