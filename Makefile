#!make

.PHONY: requirements
requirements:
	pip install -r ./requirements.txt

.PHONY: run
run:
	python3 ./prom.py
