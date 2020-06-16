#!/usr/local/bin/python3

# Create a dictionary "user_profile" with the username as the key
# value is an array of three ip/mac/user_agent combos: "profiles[]" 

# The idea is that each user probably uses [up to] 3 different
# devices on the same office subnet.

# Each of those devices will a consistent IP:MAC pair as well as
# a consistent http user_agent string. 
# TODO: make one of the devices consistent with mobile

# So now we have fake data that's almost lifelike.

# Let's generate random data all the-live-long-day
# Let's just not be completely willy-nilly about it

from randmac import RandMac
import ipaddress
import random
import configparser

cfg = configparser.ConfigParser()
cfg.read('ngids-datagen.conf')



username_count = int(cfg.get('user_profile', 'username_count'))

class make_hash:
	def __init__(self):
		self.profile_data = {}

	def make_profile_hash(username_list,useragent_list,atx_mac_ip,dfw_mac_ip,hou_mac_ip):
	# for each fname.lname pair, tie it to three uniq IP:MAC pairs in the same subnet
	# Make sure the IP:MAC pair is removed from the pool so that nobody else gets it
		ua_list = useragent_list
		user_profile = {}
		for username in username_list:
			profiles = []
			offices = [ "atx", "dfw", "hou" ]
			user_office = random.choice(offices)
			presence_count = [1, 2, 3]
			for device in presence_count:
				profile_data = {}
				if user_office == "atx":
					ip = random.choice(list(atx_mac_ip))
					profile_data["username"] = username
					profile_data["local_ip"] = str(ip)
					profile_data["mac"] = atx_mac_ip[ip]
					profile_data["user_agent"] = random.choice(ua_list)
					profiles.append(profile_data)
					atx_mac_ip.pop(ip)
					# Make sure the IP address is removed from the pool so that nobody else gets it

				elif user_office == "dfw":
					ip = random.choice(list(dfw_mac_ip))
					profile_data["username"] = username
					profile_data["local_ip"] = str(ip)
					profile_data["mac"] = dfw_mac_ip[ip]
					profile_data["user_agent"] = random.choice(ua_list)
					profiles.append(profile_data)			
					dfw_mac_ip.pop(ip)

				elif user_office == "hou":
					ip = random.choice(list(hou_mac_ip))
					profile_data["username"] = username
					profile_data["local_ip"] = str(ip)
					profile_data["mac"] = hou_mac_ip[ip]
					profile_data["user_agent"] = random.choice(ua_list)
					profiles.append(profile_data)			
					hou_mac_ip.pop(ip)

				user_profile[username] = profiles
			

		return(user_profile)


	def make_username_useragent_lists():

		last_names = cfg.get('wordlists', 'last_names')
		first_names = cfg.get('wordlists', 'first_names')
		user_agents = cfg.get('wordlists', 'user_agents')

		# create a last_names[] array
		with open(last_names, 'rt') as lnames:
			last_names = []
			for line in lnames:
				line = line.strip()
				last_names.append(line.lower())
		lnames.close()

		# create a first_names[] array
		with open(first_names, 'rt') as fnames:
			first_names = []
			for line in fnames:
				line = line.strip()
				first_names.append(line.lower())
		fnames.close()

		# create a ua_list[] array
		with open(user_agents, 'rt') as ua:
			ua_list = []
			for line in ua:
				line = line.strip()
				ua_list.append(line)
		ua.close()

		# for each last name, create a uniq first_name.last_name pair
		fname_dot_lname = []
		for x in range(0,username_count):
			lname = random.choice(last_names)
			last_names.remove(lname)
			fname = random.choice(first_names)
			full_username = fname + "." + lname
			fname_dot_lname.append(full_username)

		return(ua_list,fname_dot_lname)



	def make_mac_ip_dicts():
	# For each IP address, give it a random MAC address
	# Idea during design was to represent 3 different office locations

		# get network ranges and mac ranges from config file
		atx_cidr = cfg.get('networks', 'atx_cidr')
		dfw_cidr = cfg.get('networks', 'dfw_cidr')
		hou_cidr = cfg.get('networks', 'hou_cidr')

		atx_mac_range = cfg.get('macs', 'atx_macs')
		dfw_mac_range = cfg.get('macs', 'dfw_macs')
		hou_mac_range = cfg.get('macs', 'hou_macs')

		# Create list of IP addresses for each location		
		atx_net = ipaddress.ip_network(atx_cidr)
		dfw_net = ipaddress.ip_network(dfw_cidr)
		hou_net = ipaddress.ip_network(hou_cidr)


		# make a hash of IP to MAC address for each location
		# IPs are selected - for each in a list - no duplication
		# MACs are generated randomly, duplicates are possible
		atx_mac_ip = {}
		for ip in atx_net:
			 atx_mac = str(RandMac(atx_mac_range))
			 atx_mac_ip[ip] = atx_mac

		dfw_mac_ip = {}
		for ip in dfw_net:
			dfw_mac = str(RandMac(dfw_mac_range))
			dfw_mac_ip[ip] = dfw_mac

		hou_mac_ip = {}
		for ip in hou_net:
			hou_mac = str(RandMac(hou_mac_range))
			hou_mac_ip[ip] = hou_mac

		return(atx_mac_ip,dfw_mac_ip,hou_mac_ip)	

		# Note to self - check for duplicate MAC addresses...




