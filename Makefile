venv:
	python3 -mvenv $@
	$@/bin/pip install -r requirements.txt

requirements.txt:
	venv/bin/pip freeze | sort > $@
