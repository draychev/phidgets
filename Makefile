#!make

.PHONY: requirements
requirements:
	pip install -r ./requirements.txt

.PHONY: run
run:
	./run.sh
