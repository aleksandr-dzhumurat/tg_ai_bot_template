CURRENT_DIR = $(shell pwd)
PROJECT_NAME = tg_ai_bot
DATA_DIR = ${CURRENT_DIR}/data/db
include .env
export

prepare-dirs:
	mkdir -p ${CURRENT_DIR}/data/phoenix_data || true
	mkdir -p ${CURRENT_DIR}/data/db || true


build: prepare-dirs
	docker build -f Dockerfile \
		-t ${PROJECT_NAME}_tg:latest .

run: stop
	docker run -it --rm \
		--env-file ${CURRENT_DIR}/.env  \
		-v ${CURRENT_DIR}/src:/srv/src \
		-v ${CURRENT_DIR}/scripts:/srv/scripts \
		-v ${CURRENT_DIR}/data/db:/srv/data \
	    --name ${PROJECT_NAME}_container_tg \
		${PROJECT_NAME}_tg:latest

stop:
	docker rm -f ${PROJECT_NAME}_container_tg || true

phoenix:
	docker compose up phoenix -d

eval:
	docker run --rm \
		--env-file ${CURRENT_DIR}/.env \
		-v ${CURRENT_DIR}/src:/srv/src \
		-v ${CURRENT_DIR}/evals:/srv/evals \
		${PROJECT_NAME}_tg:latest python evals/eval_json_extraction.py

chat: phoenix
	docker run -it --rm \
		--env-file ${CURRENT_DIR}/.env  \
		-v ${CURRENT_DIR}/src:/srv/src \
		-v ${CURRENT_DIR}/scripts:/srv/scripts \
		-v ${CURRENT_DIR}/data/db:/srv/data \
	    --name ${PROJECT_NAME}_container_tg \
		${PROJECT_NAME}_tg:latest python3.12 scripts/chat.py

history:
	docker exec ${PROJECT_NAME}_container_tg python /srv/scripts/db_history.py
