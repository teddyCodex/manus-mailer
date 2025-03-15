#!/bin/bash
cd /Users/samted/Desktop/samted/Python/email-sender/manus-mailer/home/ubuntu/bulk_email_app
source venv/bin/activate
gunicorn --workers 4 --bind 0.0.0.0:5001 app:app
