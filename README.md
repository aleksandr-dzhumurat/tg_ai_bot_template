# tg_ai_bot_template
Template repo fo ChatGPT telegram bot

First, rename `evn.template` to `.env` and convigure API keys: you need access to AopenAI, Google Places and Telegram bot token

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