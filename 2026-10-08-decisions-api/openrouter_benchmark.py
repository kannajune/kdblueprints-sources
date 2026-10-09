"""Is spam checking really faster with the Decisions API? Test it through OpenRouter.

No OpenAI key needed: OpenRouter serves GPT-6 Luna both ways.
  1. Decisions:       openai/gpt-6-luna-decisions   (only answers yes or no, as a probability)
  2. Chat, one word:  openai/gpt-6-luna             (told to reply only YES or NO)
  3. Chat, normal:    openai/gpt-6-luna             (asked normally, writes a paragraph)

The same question goes to all three for every message: "Is this message spam?"
Times include the trip through OpenRouter, so they are not OpenAI's own numbers,
but all three go the same way, so the comparison is fair.

Run:
    pip install requests
    export OPENROUTER_API_KEY=sk-or-v1-...
    python openrouter_benchmark.py
"""
import os
import statistics
import sys
import time

import requests

KEY = (os.environ.get("OPENROUTER_API_KEY") or sys.exit("Set OPENROUTER_API_KEY first.")).strip().strip('"\'')
if "your-key" in KEY:
    sys.exit("OPENROUTER_API_KEY is still the example text. Put your real key in it.")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
BASE = "https://openrouter.ai/api"
QUESTION = "Is this message spam?"
MESSAGES = [
    "Congratulations! You won Rs 10 lakh. Click bit.ly/xx-win to claim now!",
    "Hi, the meeting is moved to 4 pm tomorrow. Same room.",
    "Your KYC will be blocked today. Update now at kyc-update-fast.in",
    "Amma, I reached the station. Will call you once I board.",
    "Earn Rs 5000 daily from home! No skills needed. WhatsApp now.",
    "Your Swiggy order is out for delivery.",
    "Dear customer, your account is suspended. Share OTP to reactivate.",
    "Can you send me the notes from yesterday's class?",
]

# The Decisions route is still in alpha on OpenRouter; try the alpha path first.
DECISION_PATHS = ["/alpha/decisions", "/v1/decisions"]


def check(r):
    """Stop with OpenRouter's own error message, not just the status code."""
    if r.status_code >= 400:
        sys.exit(f"OpenRouter said {r.status_code} for {r.url}:\n{r.text[:500]}")


def decisions(message):
    body = {
        "model": "openai/gpt-6-luna-decisions",
        "state": message,
        "questions": {"spam": {"type": "noul", "instructions": QUESTION,
                               "criteria": {"true": "The message is spam or a scam",
                                            "false": "A normal, genuine message"}}},
    }
    last = None
    for path in DECISION_PATHS:
        r = requests.post(BASE + path, headers=HEADERS, json=body, timeout=60)
        if r.status_code == 404:
            last = r
            continue
        check(r)
        p = r.json()["answers"]["spam"]["noul"]  # probability of yes, 0 to 1
        return f"{'YES' if p >= 0.5 else 'NO'} ({p:.2f})"
    raise RuntimeError(f"Decisions route not found: {last.status_code} {last.text[:200]}")


def chat(message, one_word):
    prompt = f"{QUESTION}\n\nMessage: {message}"
    if one_word:
        prompt += "\n\nReply with only one word: YES or NO."
    r = requests.post(BASE + "/v1/chat/completions", headers=HEADERS, timeout=120, json={
        "model": "openai/gpt-6-luna",
        "messages": [{"role": "user", "content": prompt}],
        "reasoning": {"effort": "none"},  # no hidden thinking, same as the Decisions route
    })
    check(r)
    text = r.json()["choices"][0]["message"]["content"].strip()
    return text if one_word else f"{len(text.split())} words"


def timed(fn, *args):
    start = time.perf_counter()
    out = fn(*args)
    return (time.perf_counter() - start) * 1000, out


# one warm up call each, so connection setup does not count
decisions(MESSAGES[0])
chat(MESSAGES[0], True)

runs = {"Decisions": [], "Chat, one word": [], "Chat, normal": []}
print(f"{'Decisions':>18} | {'Chat, one word':>16} | {'Chat, normal':>18} | message")
for m in MESSAGES:
    d = timed(decisions, m)
    w = timed(chat, m, True)
    n = timed(chat, m, False)
    for name, (ms, _) in zip(runs, (d, w, n)):
        runs[name].append(ms)
    print(f"{d[0]:6.0f} ms {d[1]:<10} | {w[0]:6.0f} ms {w[1]:<7} | {n[0]:6.0f} ms {n[1]:<9} | {m[:40]}")

print()
med = {k: statistics.median(v) for k, v in runs.items()}
for k, v in med.items():
    print(f"Median {k:<15} {v:6.0f} ms")
print(f"Decisions vs chat, normal:   {med['Chat, normal'] / med['Decisions']:.1f}x faster")
print(f"Decisions vs chat, one word: {med['Chat, one word'] / med['Decisions']:.1f}x faster")
