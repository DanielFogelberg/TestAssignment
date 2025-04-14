# Makefile for the OSTTRA messages REST API

.PHONY: install run clean submit fetch fetch-unread delete-single delete-multiple

install:
	python -m venv venv
	. venv/bin/activate; \
	pip install --upgrade pip; \
	pip install -r requirements.txt

run:
	. venv/bin/activate; \
	python api.py

clean:
	rm -rf venv
	rm -f instance/database.db

# make submit recipient:"bob@mail.com" message:"Hello"
submit:
	curl -X POST -H "Content-Type: application/json" \
		-d '{"recipient": "$(recipient)", "message": "$(message)"}' \
		http://127.0.0.1:5000/api/messages/

# Fetch all messages (supports optional parameters)
# Example usage: make fetch start=0 stop=10 recipient="alice@mail.com"
fetch:
	curl -X GET "http://127.0.0.1:5000/api/messages/?start=$(start)&stop=$(stop)&recipient=$(recipient)"

# Fetch only unread messages
fetch-unread:
	curl -X GET http://127.0.0.1:5000/api/messages/unread

# Delete a single message
# Example usage: make delete-single id=1
delete-single:
	curl -X DELETE http://127.0.0.1:5000/api/messages/$(id)

# Delete multiple messages (pass a JSON array of IDs)
# Example usage: make multi-delete ids='[1,2,3]'
delete-multiple:
	curl -X DELETE -H "Content-Type: application/json" \
		-d '{"ids": $(ids)}' \
		http://127.0.0.1:5000/api/messages/
