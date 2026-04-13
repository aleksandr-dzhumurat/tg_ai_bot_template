# tg_ai_bot_template
Template repo for ChatGPT telegram bot integrated with Google Maps

![bot](img/bot_image_small.png)

Works only for finding pubs, but should be extended for more categories: Concert, Restaurants, Tour, Sport, Theatre, Cinema, Arts and Culture, Family & Kids, Nightlife.

[buymeacoffee](https://buymeacoffee.com/eventally)

First, rename

```shell
mv env.template .env
```

and configure API keys: you need access to [Google Gemini](https://aistudio.google.com/), Google Places and Telegram bot token

The LLM model is configured in `src/configs/prod.yml` under `model.name` (default: `gemini-2.0-flash`).

Note: for google API keys pls visit [maps-apis](https://console.cloud.google.com/google/maps-apis/credentials)

Build docker
```shell
make build
```

To run console dialog
```shell
make chat
```

To run telegram bot
```shell
make run
```

Messages stored in sqlite db, for exploring history run
```shell
make history
```

## Evals

The `evals/` directory contains lightweight checks for the agent's core behavior.

`evals/eval_json_extraction.py` — sends a fixed phrase to the model with the system prompt and verifies that `get_json` extracts the expected structured output:

```
Country: Serbia, City: Belgrade, love craft beer: yes
→ {"city": "Belgrade", "country": "Serbia", "craft_option": true}
```

Run with:
```shell
make eval
```

Exits `0` on PASS, `1` on FAIL.
