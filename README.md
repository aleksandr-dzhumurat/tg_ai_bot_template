# tg_ai_bot_template
Template repo for ChatGPT telegram bot integrated with google maps

[buymeacoffee](https://buymeacoffee.com/eventally)

First, rename

```shell
mv env.template .env
```

and configure API keys: you need access to OpenAI, Google Places and Telegram bot token

Note: for google API keys pls visit [maps-apis](https://console.cloud.google.com/google/maps-apis/credentials)

Build docker
```shell
make build
```

To run console dialog
```shell
make run-debug
```

To run telegram bot
```shell
make run
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
