#!/usr/local/bin/python3

# This script reads a file full of URLs and does a 
# DNS lookup on each server hostname to get its IP 

# These hostname:ip pairs are then written as a JSON
# object to a local file for referencing later.

# The idea is to avoid excessive DNS lookups when
# generaring a high volume of events.

from urllib.parse import urlparse
import dns.resolver
import json
import time
import argparse
import configparser

parser = argparse.ArgumentParser(description=
    '''This script reads a file of URLs and resolves hostnames to create a file of hostname:IP JSON objects''')
parser.add_argument('-i', dest='url_file', action='store', default='./wordlists/urls.txt', help='Input file of URLs - one per line, please' )
parser.add_argument('-o', dest='json_output', action='store', default='./host2ip.txt', help='Output file for hostname:IP JSON objects')

args = parser.parse_args()

cfg=configparser.ConfigParser()


bofh = 0 # you'll know

if args.url_file:
	url_file = args.url_file
else:
	url_file = cfg.get('url_resolver', 'urls')


if args.json_output:
	json_output = args.json_output
else:
	json_output = cfg.get('url_resolver', 'json_output')


def dedupe(array):
	seen = set()
	for host in array:
		if host not in seen:
			yield host
			seen.add(host)


with open(url_file,'rt') as urls:
	url_list = []
	for line in urls:
		line = line.strip()
		url_list.append(line)
urls.close()

hostnames = []
for url in url_list:
	parsed_url = urlparse(url)
	hostname = parsed_url.hostname
	hostnames.append(hostname)

uniq_hostnames = list(dedupe(hostnames))


for host in uniq_hostnames:
	host2ip = {}
	#print(host)
	try:
		host_ip = dns.resolver.query(host, 'A')
	except:
		print("Can't resovlve hostname: " + host)
		continue
	ipval = str(host_ip[0])
	host2ip[host] = ipval
	json_pair = json.dumps(host2ip)
	print(json_pair)
	with open(json_output, 'at') as out:
		print(json_pair, file=out)
	if (bofh < 1):
		time.sleep(2)









