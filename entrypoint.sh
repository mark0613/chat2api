#!/bin/bash

# migrate
python manage.py migration upgrade

# run
python app.py
