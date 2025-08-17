#!/bin/bash
# Start script for Render deployment
exec gunicorn --bind 0.0.0.0:$PORT index:application
