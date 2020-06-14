#!/usr/local/bin/python3

from urllib.parse import urlparse
import dns.resolver
import json
import time

bofh = 0 # you'll know
urls = './urls.txt'
json_output = './host2ip.txt'

def dedupe(array):
	seen = set()
	for host in array:
		if host not in seen:
			yield host
			seen.add(host)


with open(urls,'rt') as urls:
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
		print("Can't resovlve hostname" + host)
		continue
	ipval = str(host_ip[0])
	host2ip[host] = ipval
	json_pair = json.dumps(host2ip)
	print(json_pair)
	with open(json_output, 'at') as out:
		print(json_pair, file=out)
	if (bofh < 1):
		time.sleep(2)









