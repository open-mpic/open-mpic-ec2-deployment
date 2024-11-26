#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import importlib
import time
import datetime
import threading
import subprocess
import os

def get_current_human_time():
	value = datetime.datetime.fromtimestamp(time.time())
	return value.astimezone(datetime.timezone.utc).strftime('UTC %Y-%m-%d %H:%M:%S')

def run_cmd(cmd_and_arg_list):
	#print(cmdAndArgsList)
	retry_count = 10
	out = b''
	err = b''
	for i in range(retry_count):
		p = subprocess.Popen(cmd_and_arg_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		if err == b'':
			return out.decode('utf-8')
		elif "kex_exchange_identification" in err.decode('utf-8'): # Just try again in this case.
			continue
		else:
			# Assume this is an ssh connection error.
			print(f"[{get_current_human_time()}] stderr: \"{err.decode('utf-8')}\" from cmd {cmd_and_arg_list}") # This could go to stderr or stdio.
			return out.decode('utf-8')
		#pass
		#raise IOError(f"Non-empty error: {err.decode('utf-8')}")
	print(f"[{get_current_human_time()}] Max retries ({retry_count}) reached. stderr: \"{err.decode('utf-8')}\" from cmd {cmd_and_arg_list}") # This could go to stderr or stdio.
	return out.decode('utf-8')
		

def run_cmd_at_remote(remote_ip, keyfile, cmd):
	global cmd_results
	# change to "-oStrictHostKeyChecking=accept-new" for increased security on newer systems. "-oStrictHostKeyChecking=no",
	dirname = os.path.dirname(os.path.realpath(__file__))
	res = run_cmd(["ssh", f"-i{keyfile}", "-oStrictHostKeyChecking=accept-new", f"ubuntu@{remote_ip}", cmd])
	cmd_results[remote_ip] = res
	return res


def copy_file_to_remote(local_path, remote_path, remote_ip, keyfile):
	global cmd_results
	res = run_cmd(["scp", "-r", f"-i{keyfile}", local_path, f"ubuntu@{remote_ip}:{remote_path}"])
	cmd_results[remote_ip] = res
	return res

def copy_file_from_remote(remote_path, local_path, remote_ip, keyfile):
	global cmd_results
	res = run_cmd(["scp", "-r", f"-i{keyfile}", f"ubuntu@{remote_ip}:{remote_path}", local_path])
	cmd_results[remote_ip] = res
	return res


cmd_results = {}
def run_cmd_at_remotes(remote_ips, keyfile, cmd):
	global cmd_results
	cmd_results = {}
	thread_list = []
	for remote in remote_ips:
		thread_list.append(threading.Thread(target=run_cmd_at_remote, args=(remote, keyfile, cmd)))
	for t in thread_list:
		t.start()
	for t in thread_list:
		t.join()
	return cmd_results
		
def copy_file_to_remotes(remote_ips, local_path, remote_path, keyfile):
	global cmd_results
	thread_list = []
	cmd_results = {}
	for remote in remote_ips:
		thread_list.append(threading.Thread(target=copy_file_to_remote, args=(local_path, remote_path, remote, keyfile)))
	for t in thread_list:
		t.start()
	for t in thread_list:
		t.join()
	return cmd_results