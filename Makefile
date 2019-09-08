SHELL := /bin/bash

env: installed.requirements

installed.requirements: requirements.txt yojana_env/bin/activate 
	./yojana_env/bin/python3 -m pip install -r requirements.txt --upgrade
	touch installed.requirements

yojana_env/bin/activate:
	python3 -m venv yojana_env

exe:
	./yojana_env/bin/python3  pyinstaller read_script.py

clean:
	rm -rf yojana_env
