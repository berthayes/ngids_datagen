# ngids_datagen
 Generate *real-ish looking* random data (with a smidgen of fake PII) from your Bertronix 2000 NG-Firewall and send it out via Syslog, over HTTP, Apache Kafka or plain old standard output. 

 This is handy for load testing, trying to catch SSNs off the wire, running your own example code, or developing your own apps, etc.

 ## Real-ish Looking Events
 These fake events are designed to mimic events from a NG-Firewall/IDS (presumably with MITM SSL enabled) at the border(s) of a distributed organization. 
 
 The timestamp field `ts` will be current, the hostname in the `url` field should resolve to the `remote_ip` field.  The `local_ip`, `local_mac`, and `user_agent` fields are randomly generated when the script starts, then follow the user for every generated event.  `dest_port` will be 80 or 443 depending on if the URL is http or https.

 ## Fake PII
 In addition to regular web-traffic inside->out firewall events, events will be generated that represent a junior developer testing a web application. Tests include passing customer names and SSNs via GET to a dev platform hosted in the Cloud. Your job: Find them and stop them!

 ```JSON
{
  "bytes": 4846,
  "dest_port": 80,
  "local_ip": "192.168.131.245",
  "local_mac": "b2:f4:32:69:8f:20",
  "local_port": 35001,
  "md5": "07f241fd1254765aa2647250d62a22d1",
  "method": "POST",
  "mimetype": "text/javascript",
  "proto": "tcp",
  "remote_ip": "103.242.31.33",
  "rtt": 1.257245,
  "ts": 1756934963.756185,
  "url": "http://xrea.com/eu/massa.js?lorem=venenatis&ipsum=lacinia&dolor=aenean&sit=sit&amet=amet",
  "user_agent": "Mozilla/5.0 (Windows NT 6.1; en-US) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.750.0 Safari/534.30",
  "username": "dewey.mumford"
}
```

 ### Requirements:
 Create a virtual environment for Python and install libraries

 ```sh
 python3 -m venv ./.venv
 ```
 ```sh
./.venv/bin/python3 -m pip install dnspython
./.venv/bin/python3 -m pip install randmac
./.venv/bin/python3 -m pip install kafka-python
./.venv/bin/python3 -m pip install requests
./.venv/bin/python3 -m pip install syslog_rfc5424_formatter
 ```


```
$ ./.venv/bin/python3 datagen.py -h
usage: datagen.py [-h] [-c COUNT] [-t TIME_DELAY] [-o] [-k] [-s] [-w]

This script generates a real-looking fake IDS event and sends it to your choice of Kafka, Syslog, stdout, or HTTP

options:
  -h, --help     show this help message and exit
  -c COUNT       how many events to generate and send - default is infinite
  -t TIME_DELAY  how many seconds to wait between creating events - default is 0
  -o             use to send json event to stdout
  -k             use to send json event to Kafka
  -s             use to send json event out via syslog
  -w             use to send json event out via HTTP
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