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

username_count = 10

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

		last_names = './uniq_last_names.txt'
		first_names = './uniq_first_names.txt'
		user_agents = './uniq_user_agents.txt'

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
	# for each IP address, give it a random MAC address
	# print("adding atx_mac_ip")

		atx_net = ipaddress.ip_network('172.16.0.0/20')
		dfw_net = ipaddress.ip_network('192.168.0.0/16')
		hou_net = ipaddress.ip_network('10.6.0.0/20')

		atx_mac_ip = {}
		for ip in atx_net:
			 atx_mac = str(RandMac("de:ad:b1:00:00:00"))
			 atx_mac_ip[ip] = atx_mac

		# print("adding dfw_mac_ip")
		dfw_mac_ip = {}
		for ip in dfw_net:
			dfw_mac = str(RandMac("ca:fe:b2:00:00:00"))
			dfw_mac_ip[ip] = dfw_mac

		# print("adding hou_mac_ip")
		hou_mac_ip = {}
		for ip in hou_net:
			hou_mac = str(RandMac("ba:be:b3:00:00:00"))
			hou_mac_ip[ip] = hou_mac

		return(atx_mac_ip,dfw_mac_ip,hou_mac_ip)	

		# Note to self - check for duplicate MAC addresses...




