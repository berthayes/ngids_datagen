#!/usr/local/bin/python3

import re
import random
import hashlib

args = random.randrange(2,6)

urls = './urls.txt'
with open(urls,'rt') as urls:
	url_list = []
	for line in urls:
		line = line.strip()
		url_list.append(line)
urls.close()


for url in url_list:
	start_regexp = "(^http.+?\&.*"
	middle_regexp = "?\&.*"
	end_regexp = "?[^&]+)"

	random_args = middle_regexp * args
	regexp = start_regexp + random_args + end_regexp
	shortner_url = re.compile(regexp)
	try:
		matching_url = shortner_url.match(url)
		shorter_url = matching_url.group(0)
		print(shorter_url)
	except: 
		#print("can't match URL - SORRY")
		continue