#!/usr/bin/python
# vim ~/graphite-stress.py

import sys
import time
import os
import platform
import subprocess
import socket
import pickle
import struct
from random import randint

USAGE = """
  -gs,   --graphite_server
  -jmax, --outer_loop_count
  -d,    --delay
  -p,    --port
  ./graphite-stress.py -jmax 4 -d 5 -p 2004
"""

CARBON_SERVER = 's394.ipx'
CARBON_PORT_SINGLE = 2003
CARBON_PORT_PICKLE = 2004

delay = 1
outer_loop_count = 9

if len(sys.argv) < 2:
  raise SystemExit(USAGE)

while sys.argv:
  arg = sys.argv.pop(0)
  if   arg in ['-gs'  , '--graphite_server']:
    CARBON_SERVER = sys.argv.pop(0).strip()
  elif arg in ['-jmax', '--outer_loop_count']:
    outer_loop_count = int(sys.argv.pop(0))
    print "inner loops: %d" % ( outer_loop_count )
  elif arg in ['-d', '--delay']:
    delay = int(sys.argv.pop(0))
  elif arg in ['-p', '--port']:
    CARBON_PORT_PICKLE = int(sys.argv.pop(0))
    print "pickle port: %d" % ( CARBON_PORT_PICKLE )
  else:
    dev = arg






def get_loadavg():  # For more details, "man proc" and "man uptime"
  if platform.system() == "Linux":
    return open('/proc/loadavg').read().strip().split()[:3]
  else:
    command = "uptime"  
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    os.waitpid(process.pid, 0)
    output = process.stdout.read().replace(',', ' ').strip().split()
    length = len(output)
    return output[length - 3:length]

sock_single = socket.socket()
sock_pickle = socket.socket()
myfqdn = socket.gethostname()
try:
  sock_single.connect( (CARBON_SERVER,CARBON_PORT_SINGLE) )
  sock_pickle.connect( (CARBON_SERVER,CARBON_PORT_PICKLE) )
except:
  print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT_SINGLE }
  sys.exit(1)

while True:
  for counter_x in range(1,outer_loop_count+1):
    now = int( time.time() )
    metric_timestamp  = "%d" % now
    lines2 = []
    for counter_y in range(1,100):
      for counter_z in range(1,100):
        irand = randint(1,19)
        metric_value      = 100 * counter_y + counter_z + irand
        metric_path       = "pickle.%s.m%03d.m%03d.m%03d" % (myfqdn,counter_x,counter_y,counter_z)
        # [(path, (timestamp, value)), ...]
        m = (metric_path, (metric_timestamp, metric_value))
        lines2.append(m)


    payload = pickle.dumps(lines2)
    header  = struct.pack("!L", len(payload))
    message = header + payload
    print "sending message %d %s %s %d\n" % (counter_x,metric_path,metric_timestamp,metric_value)
    #print '-' * 80
    #print message
    print
    sock_pickle.sendall(message)
    #sock_pickle.close

  time.sleep(delay)
