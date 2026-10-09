"""Route customer messages with the OpenAI Decisions API.

The AI does not write an answer. It picks one department from the list you give it,
and tells you how confident it is.

Run:
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...
    python decide.py
"""
import time

from openai import OpenAI

client = OpenAI()

DEPARTMENTS = [
    {"value": "refund", "description": "Payments, double charges, money back."},
    {"value": "delivery", "description": "Late, missing or wrongly delivered orders."},
    {"value": "complaint", "description": "Quality problems, rude service, bad experience."},
    {"value": "other", "description": "Anything that does not fit the other options."},
]

MESSAGES = [
    "I was charged twice for my order.",
    "My order was supposed to arrive yesterday and it is still not here.",
    "The dosa was cold and the delivery person was rude.",
    "Can I change the phone number on my account?",
    "The parcel was delivered to my neighbour's house.",
]

for message in MESSAGES:
    start = time.perf_counter()
    decision = client.decisions.create(
        model="gpt-6-luna",
        input=message,
        questions=[
            {
                "type": "choice",
                "name": "department",
                "instructions": "Which department should handle this customer message?",
                "choices": DEPARTMENTS,
            }
        ],
    )
    ms = (time.perf_counter() - start) * 1000
    answer = decision.answers[0]
    if answer.type == "refusal":
        print(f"{ms:6.0f} ms  refused        | {message}")
    else:
        print(f"{ms:6.0f} ms  {answer.choice:<10} {answer.confidence:.2f} | {message}")
