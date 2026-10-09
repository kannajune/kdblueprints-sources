"""Is the Decisions API really faster? Time it yourself.

Sends the same customer messages to:
  1. the Decisions API (/v1/decisions), and
  2. the Responses API with Structured Outputs, forced to pick from the same list,
both with gpt-6-luna, and compares speed and answers.

OpenAI's docs say Decisions is about 10x faster. Your numbers will depend on your
network, region and load, so run it a few times.

Run: python benchmark.py
"""
import json
import statistics
import time

from openai import OpenAI

client = OpenAI()
VALUES = ["refund", "delivery", "complaint", "other"]
DESCRIPTIONS = {
    "refund": "Payments, double charges, money back.",
    "delivery": "Late, missing or wrongly delivered orders.",
    "complaint": "Quality problems, rude service, bad experience.",
    "other": "Anything that does not fit the other options.",
}
INSTRUCTIONS = "Which department should handle this customer message?"
MESSAGES = [
    "I was charged twice for my order.",
    "My order was supposed to arrive yesterday and it is still not here.",
    "The dosa was cold and the delivery person was rude.",
    "Can I change the phone number on my account?",
    "The parcel was delivered to my neighbour's house.",
    "I cancelled the order but the money has not come back.",
    "The app shows delivered but I never got anything.",
    "Your support team was very helpful, thank you.",
]


def with_decisions(message):
    decision = client.decisions.create(
        model="gpt-6-luna",
        input=message,
        questions=[{
            "type": "choice",
            "name": "department",
            "instructions": INSTRUCTIONS,
            "choices": [{"value": v, "description": DESCRIPTIONS[v]} for v in VALUES],
        }],
    )
    answer = decision.answers[0]
    return answer.choice if answer.type == "choice" else "refused"


def with_responses(message):
    options = "\n".join(f"- {v}: {DESCRIPTIONS[v]}" for v in VALUES)
    response = client.responses.create(
        model="gpt-6-luna",
        reasoning={"effort": "none"},
        input=[
            {"role": "developer", "content": f"{INSTRUCTIONS}\n{options}"},
            {"role": "user", "content": message},
        ],
        text={"format": {
            "type": "json_schema",
            "name": "route",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"department": {"type": "string", "enum": VALUES}},
                "required": ["department"],
                "additionalProperties": False,
            },
        }},
    )
    return json.loads(response.output_text)["department"]


def timed(fn, message):
    start = time.perf_counter()
    result = fn(message)
    return (time.perf_counter() - start) * 1000, result


# one warm up call each, so connection setup does not count
with_decisions(MESSAGES[0])
with_responses(MESSAGES[0])

rows, d_times, r_times = [], [], []
for message in MESSAGES:
    d_ms, d_ans = timed(with_decisions, message)
    r_ms, r_ans = timed(with_responses, message)
    d_times.append(d_ms)
    r_times.append(r_ms)
    rows.append((d_ms, d_ans, r_ms, r_ans, message))

print(f"{'Decisions':>18} | {'Responses':>18} | message")
for d_ms, d_ans, r_ms, r_ans, message in rows:
    print(f"{d_ms:6.0f} ms {d_ans:<9} | {r_ms:6.0f} ms {r_ans:<9} | {message}")

d_med, r_med = statistics.median(d_times), statistics.median(r_times)
print()
print(f"Median Decisions: {d_med:.0f} ms")
print(f"Median Responses: {r_med:.0f} ms")
print(f"Decisions was {r_med / d_med:.1f}x faster (median)")
print(f"Same answer on {sum(1 for row in rows if row[1] == row[3])} of {len(rows)} messages")
