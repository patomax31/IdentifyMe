#!/bin/bash
# Wrapper script que ejecuta login.py con python3 del sistema
cd "$(dirname "$0")"
/usr/bin/python3 login.py "$@"
