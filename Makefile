venv:
	python3 -mvenv $@
	$@/bin/pip install -r requirements.txt
	echo "export PYTHONPATH=$$PWD" >> $@/bin/activate
	echo 'export PATH=$(shell pwd)/bin:$$PATH' >> $@/bin/activate

requirements.txt:
	venv/bin/pip freeze | sort > $@
