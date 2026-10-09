"""The three question types of the Decisions API in one request:
predicate (yes or no as a probability), choice (one option) and score (a level on a scale).

Run: python three_types.py
"""
from openai import OpenAI

client = OpenAI()

decision = client.decisions.create(
    model="gpt-6-luna",
    input="Checkout is failing for every customer. We have not processed an order in 20 minutes.",
    questions=[
        {
            "type": "predicate",
            "name": "is_bug",
            "instructions": "Is the customer reporting a software problem?",
        },
        {
            "type": "choice",
            "name": "team",
            "instructions": "Which team should handle this?",
            "choices": [
                {"value": "payments", "description": "Checkout, payments and refunds."},
                {"value": "delivery", "description": "Shipping and tracking."},
                {"value": "accounts", "description": "Login and account settings."},
                {"value": "other", "description": "Anything else."},
            ],
        },
        {
            "type": "score",
            "name": "urgency",
            "instructions": "How urgent is this?",
            "levels": [
                {"label": "Low", "description": "A suggestion or a small annoyance."},
                {"label": "Medium", "description": "Some users are affected, there is a workaround."},
                {"label": "High", "description": "Many users are blocked, business is losing money."},
            ],
        },
    ],
)

for answer in decision.answers:
    if answer.type == "predicate":
        print(f"{answer.name:<8} probability {answer.probability:.2f}")
    elif answer.type == "choice":
        print(f"{answer.name:<8} {answer.choice} (confidence {answer.confidence:.2f})")
    elif answer.type == "score":
        print(f"{answer.name:<8} score {answer.score:.2f} of 2 (confidence {answer.confidence:.2f})")
    else:
        print(f"{answer.name:<8} refused")
