ROOT=$(pwd)

PYENV=./pyenv
BIN=${PYENV}/bin
PYTHON=${BIN}/python
PIP=${BIN}/pip
NOSE=${BIN}/nosetests

GAEPATH ?= /usr/local/google_appengine
APPSERVER=${GAEPATH}/dev_appserver.py
APPCFG=${GAEPATH}/appcfg.py

PORT=8080
SRC=./


.PHONY: serve setup-dev test submodules



serve:
	${PYTHON} ${APPSERVER} --host=0.0.0.0 --port=${PORT} ${SRC}

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
	echo ${GAEPATH} >> ${PYENV}/lib/python2.7/site-packages/gae.pth
	echo ${ROOT}/lib >> ${PYENV}/lib/python2.7/site-packages/gae.pth
	echo "import dev_appserver; dev_appserver.fix_sys_path()" >> ${PYENV}/lib/python2.7/site-packages/gae.pth

	@echo "A virtual environment has been created in ${PYENV}"
	@echo "Make sure to run \"source ${BIN}\activate\""
	@echo "Make sure you have google app engine installed in ${GAEPATH}"

test:
	${PYTHON} runtests.py --with-cover --cover-package=api,main
