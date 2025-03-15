#!/bin/bash
cd /home/ubuntu/bulk_email_app
source venv/bin/activate
python waitress_server.py
