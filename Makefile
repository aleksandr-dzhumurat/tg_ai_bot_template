CURRENT_DIR = $(shell pwd)
PROJECT_NAME = tg_ai_bot
include .env
export

prepare-dirs:
	mkdir -p ${CURRENT_DIR}/data/phoenix_data || true


build:
	docker build -f Dockerfile \
		-t ${PROJECT_NAME}_tg:latest .

run:
	docker run -it --rm \
		--env-file ${CURRENT_DIR}/.env  \
		-v ${CURRENT_DIR}/src:/srv/src \
	    --name ${PROJECT_NAME}_container_tg \
		${PROJECT_NAME}_tg:latest

make stop:
	docker rm -f ${PROJECT_NAME}_container_tg || true

phoenix:
	docker compose up phoenix -d

eval:
	docker run --rm \
		--env-file ${CURRENT_DIR}/.env \
		-v ${CURRENT_DIR}/src:/srv/src \
		-v ${CURRENT_DIR}/evals:/srv/evals \
		${PROJECT_NAME}_tg:latest python evals/eval_json_extraction.py

run-debug: phoenix
	docker run -it --rm \
		--env-file ${CURRENT_DIR}/.env  \
		-v ${CURRENT_DIR}/src:/srv/src \
		-v ${CURRENT_DIR}/scripts:/srv/scripts \
	    --name ${PROJECT_NAME}_container_tg \
		${PROJECT_NAME}_tg:latest python scripts/chat.py
