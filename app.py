import os
from typing import Callable

import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

APP_TOKEN = "xapp-1-A05C7A7GFG8-5405177267601-..."
BOT_TOKEN = "xoxb-268250784917-..."
COMPLETIONS_MODEL = "text-davinci-002"
COMPLETIONS_API_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 300,
    "model": COMPLETIONS_MODEL,
}
app = App(token=BOT_TOKEN)


@app.event("app_mention")
def mention_handler(body: dict, say: Callable):
    import pdb; pdb.set_trace()
    sender_id = f"<@{body.get('event', {}).get('user')}>"
    bot_id = body.get("event", {}).get("text").split()[0]
    message = body.get("event", {}).get("text")
    message = message.replace(bot_id, "").strip()
    if message:
        answer = get_answer(message)
        say(f"Hey {sender_id}: {answer}")

def get_answer(message: str):
    # response = openai.Completion.create(prompt=message, **COMPLETIONS_API_PARAMS)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=message,
        temperature=0.5,
        max_tokens=256,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    import pdb; pdb.set_trace()
    return response["choices"][0]["text"].strip(" \n")

openai.api_key = 'sk-xmBLbTO6yOhJz...'




@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")



if __name__ == "__main__":
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()