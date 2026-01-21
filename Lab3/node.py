#!/usr/bin/env python3
import threading
import time
import random
import argparse
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Global variables
lock = threading.Lock()
state = 'Follower'
currentTerm = 0
votedFor = None
log_entries = []
commitIndex = 0
lastApplied = 0
nextIndex = {}
matchIndex = {}
votes = 0
stop_threads = False
heartbeat_interval = 0.1
election_timeout = 0.15
NODE_ID = None
PORT = None
PEERS = []

def log_line(msg):
	print(f"[{NODE_ID}] {msg}")


def handle_election_victory():
	global state, votes, nextIndex, matchIndex, log_entries, currentTerm
	# majority? (ceil((N)/2))
	if votes >= (len(PEERS)+1)//2 + 1:
		with lock:
			state = 'Leader'
			# initialize leader state
			for pid, url in PEERS:
				nextIndex[pid] = len(log_entries)
				matchIndex[pid] = -1
			log_line(f"Received votes → Leader (term {currentTerm})")
	else:
		# stay follower/candidate and wait for next timeout
		state = 'Follower'
		votedFor = None
		last_heartbeat = time.time()


def heartbeat_thread():
	global state, stop_threads
	while not stop_threads:
		time.sleep(heartbeat_interval)
		with lock:
			if state == 'Leader':
				# send heartbeats (AppendEntries with empty entries)
				for pid, url in PEERS:
					try:
						payload = {'term': currentTerm, 'leaderId': NODE_ID, 'entries': [], 'leaderCommit': commitIndex}
						requests.post(url + '/append_entries', json=payload, timeout=0.5)
					except Exception:
						pass


def election_timer_thread():
	"""Placeholder for election timer logic"""
	pass


def start_background_threads():
	t1 = threading.Thread(target=election_timer_thread, daemon=True)
	t2 = threading.Thread(target=heartbeat_thread, daemon=True)
	t1.start()
	t2.start()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--id', required=True, dest='id')
	parser.add_argument('--port', type=int, required=True)
	parser.add_argument('--peers', default='')
	args = parser.parse_args()

	NODE_ID = args.id
	PORT = args.port
	# parse peers as CSV of id:host:port or id:port (assume localhost)
	peers_raw = args.peers.split(',') if args.peers else []
	PEERS = []
	for p in peers_raw:
		p = p.strip()
		if not p:
			continue
		if ':' in p:
			pid, port_or_host = p.split(':', 1)
			# allow host:port or just port
			if port_or_host.isdigit():
				host = 'http://127.0.0.1:' + port_or_host
			else:
				host = 'http://' + port_or_host
			PEERS.append((pid, host))
		else:
			# treat as id with default port mapping
			PEERS.append((p, 'http://127.0.0.1:8000'))

	# randomize election timeout between 0.15 and 0.3 seconds
	election_timeout = random.uniform(0.15, 0.3)
	last_heartbeat = time.time()

	start_background_threads()
	app.run(host='0.0.0.0', port=PORT, threaded=True)