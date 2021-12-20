#!/bin/bash

FLASK_APP=blurg.server.__main__ FLASK_ENV=development SECRET_KEY=CHANGE_KEY_HERE python -m flask run --host=0.0.0.0
