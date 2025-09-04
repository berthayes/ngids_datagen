#!/usr/local/bin/python3

import random
import logging
import logging.handlers
from logging.handlers import SysLogHandler
from syslog_rfc5424_formatter import RFC5424Formatter
import ipaddress
from randmac import RandMac
from urllib.parse import urlparse
import dns.resolver
import re
import hashlib
import time
import json
from kafka import KafkaProducer
import user_profile_hash_maker as uphm
import argparse
import configparser
import requests


# Parse command line arguments
parser = argparse.ArgumentParser(description=
    '''This script generates a real-looking fake IDS event and sends it to your choice of Kafka, Syslog, stdout, or HTTP''')
parser.add_argument('-c', dest='count', action='store', default=-1, help='how many events to generate and send - default is infinite' )
parser.add_argument('-t', dest='time_delay', action='store', default=0, help='how many seconds to wait between creating events - default is 0')
parser.add_argument('-o', dest='output', action='store_true', help='use to send json event to stdout')
parser.add_argument('-k', dest='kafka', action='store_true', help='use to send json event to Kafka')
parser.add_argument('-s', dest='syslog', action='store_true', help='use to send json event out via syslog')
parser.add_argument('-w', dest='httpout', action='store_true', help='use to send json event out via HTTP')
args = parser.parse_args()

# Check for syslog output and set values once
if args.syslog:
	logger = logging.getLogger('syslog-ng')
	logger.setLevel(logging.INFO)
	handler = SysLogHandler(facility=SysLogHandler.LOG_USER, address=("10.100.0.200",9514))
	logger.addHandler(handler)

# Parse configs
cfg = configparser.ConfigParser()
cfg.read('ngids-datagen.conf')
urls = cfg.get('wordlists', 'urls')
mimetypes = cfg.get('wordlists', 'mimetypes')
host2ip = cfg.get('wordlists', 'host2ip')
bootstrap_servers = cfg.get('kafka', 'bootstrap-servers')
topic = cfg.get('kafka', 'topic')
test_user_info = cfg.get('developer', 'test_user_info')
endpoint = cfg.get('http_output', 'endpoint')

def to_kafka(data):
	# [mostly] From https://kafka-python.readthedocs.io/en/master/usage.html
	# Asynchronous by default
	producer = KafkaProducer(bootstrap_servers=[bootstrap_servers])
	future = producer.send(topic, data.encode('utf-8'))

	# Block for 'synchronous' sends
	try:
		record_metadata = future.get(timeout=100)
	except KafkaError:
		# Decide what to do if produce request failed...
		log.exception()
		pass

def http_output(data):
	print("sending to " + endpoint)
	response = requests.post(endpoint, data)
	print(response.status_code)



def make_event(profile):
	ids_event = {}
	# select a random user
	username = random.choice(list(user_profile))
	# select an ip:mac:useragent combo
	rando_profile = random.choice(user_profile[username])
	# generate a NOW epoch.milliseconds timestamp
	now_millis = (time.time())
	# randomly select a URL fromthe list
	ids_event["url"] = random.choice(url_list)
	# determine dest_port based on http(s)
	if re.match(r'^https', ids_event["url"]):
		dest_port = 443
	else:
		dest_port = 80

	parsed_url = urlparse(ids_event["url"])
	hostname = parsed_url.hostname
	
	try:
		ipval = host2ip_dict[hostname]
	except:
		print("hash lookup failed")
		try:
			host_ips = dns.resolver.query(hostname, 'A')
			ipval = str(host_ips[0])
		except:
			print("Can't resolve this hostname " + hostname)
			pass
	else:
		try:
			ids_event["remote_ip"] = ipval
			ids_event["username"] = username
			ids_event["local_ip"] = rando_profile["local_ip"]
			ids_event["local_mac"] = rando_profile["mac"]
			ids_event["user_agent"] = rando_profile["user_agent"]
			ids_event["dest_port"] = dest_port
			ids_event["local_port"] = random.randrange(1024,65535)
			ids_event["rtt"] = round(random.uniform(0.5, 1.9), 6)
			ids_event["bytes"] = random.randrange(200,6000)
			ids_event["method"] = random.choice(["GET","POST"])
			ids_event["proto"] = "tcp"
			ids_event["mimetype"] = random.choice(mimetypes_list)
			ids_event["ts"] = now_millis

			event_hash = hashlib.md5(str(ids_event).encode())
			ids_event["md5"] = event_hash.hexdigest()

		except:
			print("I am slain!")
			exit()
	sorted_event = dict(sorted(ids_event.items()))
	return(sorted_event)

def make_developer_event():
	# Make a custom event for our developer
	ids_event = {}
	ids_event["username"] = "Iam Developer"
	ids_event["local_ip"] =  "10.100.99.86"
	ids_event["local_mac"] = "ca:fe:de:ad:be:ef"
	ids_event["user_agent"] = "PostmanRuntime/7.39.0"
	ids_event["dest_port"] = 443
	ids_event["local_port"] = random.randrange(1024,65535)
	ids_event["rtt"] = round(random.uniform(0.5, 1.9), 6)
	ids_event["bytes"] = random.randrange(200,6000)
	ids_event["ts"] = (time.time())
	test_info = random.choice(user_info)
	ids_event["url"] = "https://dev.retirement.tnwa.texas.gov/how-much-longer?" + test_info
	ids_event["method"] = "GET"
	ids_event["proto"] = "tcp"
	ids_event["mimetype"] = "-"
	ids_event["remote_ip"] = "52.37.243.89"

	event_hash = hashlib.md5(str(ids_event).encode())
	ids_event["md5"] = event_hash.hexdigest()	

	sorted_event = dict(sorted(ids_event.items()))
	return(sorted_event)

# create a urls[] array
with open(urls,'rt') as urls:
	url_list = []
	for line in urls:
		line = line.strip()
		url_list.append(line)
urls.close()

# create a mimetipes_list[] array
with open(mimetypes, 'rt') as mimetypes:
	mimetypes_list = []
	for line in mimetypes:
		line = line.strip()
		mimetypes_list.append(line)
mimetypes.close()

# create a hostname:ip hash to reference instead of using DNS
host2ip_dict = {}
try:
	with open(host2ip, 'rt') as host2ip:
		for line in host2ip:
			line_dict = {}
			line = line.strip()
			line_dict = json.loads(line)
			for hostname, ip in line_dict.items():
				host2ip_dict[hostname] = ip
	host2ip.close()
except:
	print("Can't open host2ip file")
	print("Use the url_host_resolver.py script to create a host2ip.txt file")
	exit()	

# Call the user_profile_hash_maker.py script to make a dictionary of users and their devices
# In this way user:ip:mac mappings should stay consistent despite randomly generated data
[useragent_list, username_list] = uphm.make_hash.make_username_useragent_lists()
[atx_mac_ip, dfw_mac_ip, hou_mac_ip] = uphm.make_hash.make_mac_ip_dicts()
user_profile = uphm.make_hash.make_profile_hash(username_list, useragent_list, atx_mac_ip, dfw_mac_ip, hou_mac_ip)

# Create a list of test users and SSNs - these are used by jr. developer in app testing
with open(test_user_info, 'rt') as test_user_info:
	user_info = []
	for line in test_user_info:
		line = line.strip()
		user_info.append(line.lower())
	test_user_info.close()


# Main loop
count = 0
while 1:
	count += 1
	# make one developer event every 25 events
	if count % 25 == 0:
		ids_event = make_developer_event()
	else:
		ids_event = make_event(user_profile)
	json_event = json.dumps(ids_event)
	if args.output:
		print(json_event)
	if args.syslog:
		logger.info(json_event)
	if args.httpout:
		try:
			http_output(json_event)
		except: print("Can't send event via HTTP")
	if args.kafka:
		try:
			to_kafka(json_event)
		except:
			print("Can't send event to Kafka")
	if int(args.count):
		if count == int(args.count):
			exit()
	else:
		if count == 250:
			count = 0		
	if int(args.time_delay) > 0:
		time.sleep(int(args.time_delay))