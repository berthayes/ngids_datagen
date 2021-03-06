#!/usr/local/bin/python3

import random
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

# Parse configs
cfg = configparser.ConfigParser()
cfg.read('ngids-datagen.conf')


# Parse args - get money
parser = argparse.ArgumentParser(description=
    '''This script generates a real-looking fake IDS event and sends it to your Kafka cluster''')
parser.add_argument('-c', dest='count', action='store', default=-1, help='how many events to generate and send to Kafka - default is infinite' )
parser.add_argument('-t', dest='time_delay', action='store', default=0, help='how many seconds to wait between creating events - default is 0')
parser.add_argument('-o', dest='output', action='store_true', help='use to send json event to stdout')

args = parser.parse_args()

urls = cfg.get('wordlists', 'urls')
mimetypes = cfg.get('wordlists', 'mimetypes')
host2ip = cfg.get('wordlists', 'host2ip')
bootstrap_servers = cfg.get('kafka', 'bootstrap-servers')
topic = cfg.get('kafka', 'topic')



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
	return(ids_event)

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

# create NGFW/IDS Event, I guess...
if int(args.count) > 0:
	count = int(args.count)
	for x in range(0, count):
		if int(args.time_delay) > 0:
			time.sleep(int(args.time_delay))
		ids_event = make_event(user_profile)
		json_event = json.dumps(ids_event)
		if args.output:
			print(json_event)
		try:
			to_kafka(json_event)
		except:
			print("Can't send event to Kafka")
else:
	while 1:
		if int(args.time_delay) > 0:
			time.sleep(int(args.time_delay))
		ids_event=make_event(user_profile)	
		json_event = json.dumps(ids_event)
		if args.output:
			print(json_event)
		try:
			to_kafka(json_event)
		except:
			print("Can't send event to Kafka")
			
