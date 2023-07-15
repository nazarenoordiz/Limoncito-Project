import os
from typing import Callable

import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

class Limoncito:
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    COMPLETIONS_MODEL = "text-davinci-002"
    COMPLETIONS_API_PARAMS = {
        "temperature": 0.0,
        "max_tokens": 300,
        "model": COMPLETIONS_MODEL,
    }
    app = App(token=SLACK_BOT_TOKEN)
    
    def __init__(self):
        pass

    @app.event("app_mention")
    def mention_handler(self, body: dict, say: Callable):
        sender_id = f"<@{body.get('event', {}).get('user')}>"
        bot_id = body.get("event", {}).get("text").split()[0]
        message = body.get("event", {}).get("text")
        message = message.replace(bot_id, "").strip()
        if message:
            answer = self.get_answer(message)
            say(f"Hey {sender_id}: {answer}")

    def get_answer(self, message: str) -> str:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=message,
            temperature=0.5,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response["choices"][0]["text"].strip(" \n")

    @app.message("hello")
    def message_hello(self, message: str, say: Callable) -> str:
        # say() sends a message to the channel where the event was triggered
        say(f"Hey there <@{message['user']}>!")

    if __name__ == "__main__":
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()