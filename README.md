# GAE CSV Upload Application [![Build Status](https://travis-ci.org/SingaporeClouds/education.png?branch=master)](https://travis-ci.org/SingaporeClouds/education)

## Setup

Requirements:
- python2.7
- virtualenv
- google app engine install in /usr/local/google_appengine.

You can then setup you virtual environement:
```
virtualenv pyenv
pip install -r dev-requirements.txt
echo /usr/local/google_appengine >> pyenv/lib/python2.7/site-packages/gae.pth
echo `pwd`/lib >> pyenv/lib/python2.7/site-packages/gae.pth
echo "import dev_appserver; dev_appserver.fix_sys_path()" >> pyenv/lib/python2.7/site-packages/gae.pth
```

or

```
make setup-dev
```

Remember to activate the virtual environement when working on the project:
```
source pyenv/bin/activate
```

## Depedencies

Depedencies are installed with pip, and should be installed inside the 
lib folder (using the `-t` option) if they need to be uploaded:

```
pip install somelibrary -t lib
```

Please keep the list of depedencies in `requirements.txt` up to date.

Note: that libraries only needed for testing should be installed normally
(in the pyenv site-package folder) and be listed in dev-requirements.txt)


## Tests

```
python runtests.py
```

or

```
make test
```