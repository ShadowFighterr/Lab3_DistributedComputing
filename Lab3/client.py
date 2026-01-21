#!/usr/bin/env python3
import argparse
import requests
import time

parser = argparse.ArgumentParser()
parser.add_argument('--leader', required=True, help='Leader URL, e.g. http://127.0.0.1:8000')
parser.add_argument('--cmd', required=True, help='Command to send, e.g. "SET x=5"')
args = parser.parse_args()

url = args.leader.rstrip('/') + '/client_cmd'
try:
	r = requests.post(url, json={'cmd': args.cmd}, timeout=2)
	print('Response:', r.status_code, r.text)
except Exception as e:
	print('Error:', e)