# OpenAI Decisions API: try it yourself

From the KD Blueprints Short about OpenAI's Decisions API (October 2026).

In the video: you ask the AI "Is this message spam?" and the AI writes a full paragraph, when you only wanted
one word, Yes or No. With the Decisions API the AI answers in just one word, so the AI replies up to 10x faster.
Here you can check that claim with your own key.

## What is in this folder

| File | What it does |
|---|---|
| [spam_benchmark.py](spam_benchmark.py) | **The video's example.** Asks "Is this message spam?" three ways (Decisions API, chat told to reply in one word, normal chat) and times each |
| [openrouter_benchmark.py](openrouter_benchmark.py) | The same spam test through OpenRouter, if you have an OpenRouter key instead of an OpenAI key |
| [decide.py](decide.py) | Sends 5 customer messages and gets back one department each: refund, delivery, complaint or other |
| [three_types.py](three_types.py) | One request that asks all three question types: yes or no, pick one, and a score |
| [benchmark.py](benchmark.py) | Times the same messages on the Decisions API and on the Responses API, and prints the speedup |
| [sample-output.txt](sample-output.txt) | Output from our real run on 9 Oct 2026, so you can see what to expect |
| [SOURCES.md](SOURCES.md) | Every fact in the video with its source |

## Our result (9 Oct 2026)

Same question, "Is this message spam?", on 8 messages:

| Way | Median time | Answer |
|---|---|---|
| Decisions API | **0.19 s** | YES or NO, all 8 right |
| Chat, told to reply in one word | 7.8 s | YES or NO, all 8 right |
| Chat, asked normally | 8.6 s | a 13 to 48 word paragraph |

Normal chat was 1 to 3 s for the first messages and 8 to 10 s later in the run, so the speed-up
ranged from about 5x to over 40x. Full output: [sample-output.txt](sample-output.txt).

## Run it

You need Python 3.9 or newer and an OpenAI API key with access to the Decisions API (public beta).

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python spam_benchmark.py
python decide.py
python three_types.py
python benchmark.py
```

Each script makes a handful of small calls. The Decisions API charges only for input tokens
(about $0.10 per 1M), so a full run costs a tiny fraction of a cent. The benchmark also calls the
Responses API, which charges as usual.

## What you should see

`decide.py` prints the time, the chosen department and the confidence for each message:

```
   ... ms  refund     0.97 | I was charged twice for my order.
```

`benchmark.py` ends with a summary like:

```
Median Decisions: ... ms
Median Responses: ... ms
Decisions was ...x faster (median)
```

Your numbers will not match ours exactly. Speed depends on your network, your region and how busy
the servers are. Run it a few times. If you get something very different, open an issue and tell us.

## If it fails

- `AttributeError: 'OpenAI' object has no attribute 'decisions'`: your SDK is too old. Run `pip install -U openai` (3.26.0 or newer).
- An error saying the Decisions API is not enabled: it is a public beta and access can take time to reach every account. Check the [playground](https://platform.openai.com/decisions).
- `401`: your API key is missing or wrong.

## How it works, in one line

Normal chat APIs write an answer word by word. The Decisions API only has to pick one of the
options you gave it, so there is nothing long to write, and that is where the speed comes from.

Official guide: https://developers.openai.com/api/docs/guides/decisions
