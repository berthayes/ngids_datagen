# ngids_datagen
 Generate random data from your Bertronix 2000 Firewall and send them to Apache Kafka.

 This is Yet Another Random Data Generator.  There are others like it, but this one is mine.  This DG will create *real-ish looking* events from a fictional Next-Gen Firewall/IDS/IPS.

 This is handy for load testing, running your own example code, or developing your own apps, etc.

 ## Real-ish Looking Events
 The timestamp field `ts` will be current, the hostname in the `url` field should resolve to the `remote_ip` field.  The `local_ip`, `local_mac`, and `user_agent` fields are randomly generated when the script starts, then follow the user for every generated event.  `dest_port` will be 80 or 443 depending on if the URL is http or https.

 ```JSON
 {
  "url": "https://myspace.com/ligula/in.xml?eleifend=aenean&quam=auctor&a=gravida&odio=sem&in=praesent",
  "remote_ip": "63.135.90.70",
  "username": "nila.younger",
  "local_ip": "192.168.14.152",
  "local_mac": "'ca:fe:b2:87:c3:df'",
  "user_agent": "Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/ 20120405 Firefox/14.0.1",
  "dest_port": 443,
  "local_port": 51763,
  "rtt": 1.166855,
  "bytes": 5973,
  "method": "POST",
  "proto": "tcp",
  "mimetype": "application/rtf",
  "ts": 1592127451.520935,
  "md5": "06180dd3c0fce2c8cc2d6dd89b1b20cf"
}
```

 ### Requirements:
 ```
 $ sudo apt-get install python3-pip

$ pip3 install dnspython
$ pip3 install randmac
$ pip3 install kafka
```

```
$ ./datagen.py -h
usage: datagen.py [-h] [-c COUNT] [-t TIME_DELAY]

This script generates a real-looking fake IDS event and sends it to your Kafka
cluster

optional arguments:
  -h, --help     show this help message and exit
  -c COUNT       how many events to generate and send to Kafka - default is
                 infinite
  -t TIME_DELAY  how many seconds to wait between creating events - default is
                 0
```



The datagen.py script looks for a file called ```host2ip.txt``` by default that contains a list of hostname:ip mappings as JSON objects.  These are (at the time of this writing) real hostname to IP mappings.

Use the url_host_resolver.py script to read a file containing a list of URLs and lookup the IP address for the corresponding hostname.  This script will re-create the ```host2ip.txt``` file if/when needed.

```
$ ./url_host_resolver.py -h
usage: url_host_resolver.py [-h] [-i URLS] [-o JSON_OUTPUT]

This script reads a file of URLs and resolves hostnames to create a file of
hostname:IP JSON objects

optional arguments:
  -h, --help      show this help message and exit
  -i URLS         Input file of URLs - one per line, please
  -o JSON_OUTPUT  Output file for hostname:IP JSON objects
```


user_profile_hash_maker.py is a script that creats a dictionary of usernames to MAC:IP:user_agent strings.  This is to make the fake data look a little more life-like.  The idea is that each user will have used 3 different devices on the same LAN, so generated data should reflect this and not give a completely random combination of username,mac,ip,user_agent for every event generated.  This script is called from the datagen.py script.