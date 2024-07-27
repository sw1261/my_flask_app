#!/bin/sh

celery -A app.celery worker --loglevel=info
