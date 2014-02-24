ROOT=`pwd`

PYENV=./pyenv
BIN=${PYENV}/bin
PYTHON=${BIN}/python
PIP=${BIN}/pip
NOSE=${BIN}/nosetests

GAE=/usr/local/google_appengine
APPSERVER=${GAE}/dev_appserver.py
APPCFG=${GAE}/appcfg.py

PORT=8080
SRC=./


.PHONY: serve setup-dev test submodules

serve:
	open "http://localhost:${PORT}"
	${PYTHON} ${APPSERVER} --port=${PORT} ${SRC}

submodules:
	git submodule update --init 
	git submodule foreach git stash
	git submodule foreach git pull origin master

setup-dev:
	# create python virtual environment
	virtualenv ${PYENV}

	# install dependencies
	${PIP} install -r dev-requirements.txt

	# add GAE to path
	echo ${GAE} >> ${PYENV}/lib/python2.7/site-packages/gae.pth
	echo ${ROOT}/lib >> ${PYENV}/lib/python2.7/site-packages/gae.pth
	echo "import dev_appserver; dev_appserver.fix_sys_path()" >> ${PYENV}/lib/python2.7/site-packages/gae.pth

	@echo "A virtual environment has been created in ${PYENV}"
	@echo "Make sure to run \"source ${BIN}\activate\""
	@echo "Make sure you have google app engine installed in ${GAE}"

test:
	cd  ${SRC}; PYTHONPATH=${SRC} ${NOSE} --with-gae --without-sandbox -w unittests --gae-application=${SRC} --with-coverage --cover-package=main,models
