template = """#!/bin/bash 
#-xe

export DIR_VENV=$PWD/_venv
export FLASK_APP=entrypoint.py

if [ -d "$DIR_VENV" ]; then
  source $DIR_VENV/bin/activate
fi

cmd_install() {
  # cmd_install. Tambien se puede usar para actualizar & agregadas librerias
  if [ ! -d "$DIR_VENV" ]; then
    # sudo apt-get install python3-venv -y
    python3 -m venv $DIR_VENV
    source $DIR_VENV/bin/activate
  fi
  
  if [ -f "requirements-lock.txt" ]; then
    pip install -r requirements-lock.txt
  fi

  pip install -r requirements.txt
  pip freeze -r requirements.txt > requirements-lock.txt
}

cmd_add() {
  # agregar paquetes
  pip install $@
  pip freeze -r requirements.txt > requirements-lock.txt
}

cmd_add-mg() {
  # agregar paquetes & buscarlo primero en el pypi maujagroup 
  pip install $@ -i http://pypi.maujagroup.com:8080/simple\
    --trusted-host pypi.maujagroup.com\
    --extra-index-url https://pypi.org/simple

  pip freeze -r requirements.txt > requirements-lock.txt
}

cmd_lock() {
  # crear lock
  pip freeze -r requirements.txt > requirements-lock.txt
}

cmd_del() {
  # agregar paquetes
  pip uninstall $@
  pip freeze -r requirements.txt > requirements-lock.txt
}


cmd_web() { 
  export ENVFILE=.env
  export FLASK_ENV=development
  flask run
}

cmd_webdev() { 
  export ENVFILE=.env.dev
  flask run
}

cmd_flask() { 
  flask "$@" 
}

cmd_cmd() { 
  flask cmd "$@" 
}


cmd_db() { 
  flask db "$@" 
}

cmd_pip() { 
  pip "$@" 
}

cmd_pos-commit() { 
  echo "pos-commit";
}

cmd_version() {
  # python --version
  flask --version
  pip --version
}

cd "$(dirname "$0")"; _cmd="${1?"cmd is required"}"; shift; "cmd_${_cmd}" "$@"
"""
