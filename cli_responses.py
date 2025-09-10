#!/usr/bin/env python3
# cli_responses.py - very small terminal chatbot using OpenAI Responses API

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def main():
    #Reads the API key from environment variable.
    api_key = os.environ.get("OPENAI_API_KEY") 
    if not api_key:
        print("Set OPENAI_API_KEY in your environment.")
        return

    #Creates a client object, chooses a model (gpt-4o-mini is fast & cheap).
    client = OpenAI(api_key=api_key)  # uses the official SDK
    model = "gpt-4o-mini"  # pick a model you have access to

    # initial instruction / system behaviour
    system_instruction = "You are a concise, friendly assistant that helps with programming topics."

    # input history in Responses API format
    history = [
        {"role": "system", "content": [{"type": "input_text", "text": system_instruction}]}
    ]

    print("CLI chatbot (Responses API). Type 'exit' or Ctrl-C to quit.")
    #Takes user input from terminal and appends it to conversation history.
    while True:
        try:
            user = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not user:
            continue
        if user.lower() in ("exit", "quit"):
            break

        # append user input
        history.append({"role": "user", "content": [{"type": "input_text", "text": user}]})

        '''# call Responses API
        resp = client.responses.create(
            model=model,
            input=history,
            # optional tweaks:
            # temperature=0.6,
            # max_output_tokens=512,
        )

        # SDK exposes a convenient text accessor
        assistant_text = getattr(resp, "output_text", None) or ""
        print("\nAssistant:", assistant_text.strip())
        '''
         # Start streaming
        print("\nAssistant: ", end="", flush=True)
        full_reply = ""

        with client.responses.stream(
            model=model,
            input=history,
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    # Print new tokens as they come
                    print(event.delta, end="", flush=True)
                    full_reply += event.delta
                elif event.type == "response.completed":
                    # Done streaming
                    break

            # Get the final full response object
            response = stream.get_final_response()

        # append assistant reply to history so next turn is contextual
        #history.append({"role": "assistant", "content": [{"type": "output_text", "text": assistant_text}]})
        history.append({"role": "assistant", "content": [{"type": "output_text", "text": full_reply}]})

if __name__ == "__main__":
    main()
