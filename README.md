# GAE CSV Upload Application [![Build Status](https://travis-ci.org/SingaporeClouds/education.png?branch=master)](https://travis-ci.org/SingaporeClouds/education)

## Setup

Requirements:
- python2.7
- virtualenv

Install/update google app engine
```
cd ~
rm -rf .google_appengine
wget http://googleappengine.googlecode.com/files/google_appengine_1.8.9.zip
unzip google_appengine_1.8.9.zip
mv google_appengine .google_appengine
rm google_appengine_1.8.9.zip
```

Add google appengine to your path (skip it in nitrous.io):
```
echo "export PATH=$PATH:$HOME/.google_appengine" >> ~/.bashrc
```

Define the GAEPATH variable (it will be used by the test runner):
```
echo "export GAEPATH=$HOME/.google_appengine" >> ~/.bashrc
source ~/.bashrc
```


You can then setup you virtual environement:
```
virtualenv pyenv
pip install -r dev-requirements.txt
echo $GAEPATH >> pyenv/lib/python2.7/site-packages/gae.pth
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