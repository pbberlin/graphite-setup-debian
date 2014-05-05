#!/usr/bin/python

'''
requires
pip install requests
pip install graphitesend
pip install Werkzeug

This scripts duplicates all branches below
 /carbon_root/prefix_from 
    to 
 /carbon_root/prefix_to 

In our graphite world, the branches are the host names.


Todo:
Make prefix_from  and prefix_t command line args.
Make src and target graphite server into command line arguments.


'''



import sys

import json, requests, os

from werkzeug.datastructures import MultiDict    # to have repeatable get params

import graphitesend

from datetime import *
import time

it_max_hosts   = 33333    # reduce limit for testing

graphite_server_dns = 'graphite.ipx'


prefix_from = "servers."
prefix_to   = "servers2."


sleep_seconds = 15

usage_msg = """usage: 
   param 1 - graphite host
   param 2 - date  - yyyy-mm-dd
   param 3 - number of days ahead, optional, default 1
   example
   ./duplicate_metrics.py  graphite.ipx  2014-03-03  3
  
"""

print usage_msg


number_of_arguments =  len(sys.argv)
if number_of_arguments <= 3:
   print "insufficient params\n"
   exit(0)






def migrate_one_server( srv ):
   
   params_get_params_unique  = {
      'target':'t1'  ,
      'target':'t2'
   }

   params2  = MultiDict([
      ('1', '2'), 
      ('1', '3')
   ])

   params2  = MultiDict([
      ('format' , 'json'                             ),
      ('target' , prefix_from + srv + '.*.*.*.*.*'   ),
      ('target' , prefix_from + srv + '.*.*.*.*'     ),
      ('target' , prefix_from + srv + '.*.*.*'       ),
      ('target' , prefix_from + srv + '.*.*'         ),
      ('from_old' , '-144minutes'                    ),
      ('from'  , str_day_start                       ),
      ('until' , str_day_end                         )
   ])

   # I needed to submit multiple similar get params to graphite API.
   # No, an array-param does not work.
   # All I tried was in vain.
   # The only way to submit repetitive get params is by concatenating them on the url
   params2 = {}

   url= 'http://'+ graphite_server_dns +'/render/'
   url= 'http://'+ graphite_server_dns +'/render/?format=json'
   url += '&target='+ prefix_from + srv + '.*.*.*.*.*'
   url += '&target='+ prefix_from + srv + '.*.*.*.*'
   url += '&target='+ prefix_from + srv + '.*.*.*'
   url += '&target='+ prefix_from + srv + '.*.*'
   url += '&from='  + str_day_start
   url += '&until=' + str_day_end

   resp = requests.get(url=url, params=params2)
   data = json.loads(resp.content)
    
   #print data
   
   count_targets = len(data)
      
   print "json data loaded - Anzahl targets: ", count_targets
   #print data[1]['target']
   #print data[1]['datapoints']
   

   i1 = 0
   data_by_timestamp = {}
   for metric in data:
      tg = metric['target']
      tg = tg.replace( prefix_from , prefix_to  );

      if i1 < 4 :
         print tg
      if i1 == 4:
         print "..."

      #print metric['datapoints']
      i11 = 0
      for dp in metric['datapoints']:
         ts = dp[1]
         mv = dp[0]
         i11+=1
         if i11  < 4  and i1 < 4:
            print ts,mv
         if i11 == 4  and i1 < 4:
            print "..."
         if mv == 'None' or mv is None :
            #print 'skipping Null - None ', mv
            continue
         #g.send( tg, float(mv), ts )    # this would be single pickle sender

         if str(ts) in data_by_timestamp:
            data_by_timestamp[str(ts)].update( {tg:mv} )   # append metric + value
         else:
            data_by_timestamp[str(ts)]= {tg:mv}            # first  metric + value
      i1+=1
      if i1 > 5000:
         print "more than 5000 metrics for one host - check this"
         sys.exit(0)
 

   #print data_by_timestamp
   print "send by timestamp"

  #g = graphitesend.init( graphite_server=graphite_server_dns , prefix=prefix_to, system_name=srv )
   g = graphitesend.init( graphite_server=graphite_server_dns , prefix='', system_name='' )

   i3=0
   for lp_ts in data_by_timestamp:
      i3+=1
      if i3 < 4 :
        print 'sending ts data' , lp_ts
        print '    '  +   str(data_by_timestamp[lp_ts])[:110] + " ... "
      g.send_dict( data_by_timestamp[lp_ts], int(lp_ts) )  


   graphitesend.reset()

   return



def get_nodes_under_prefix_from():

   url= 'http://'+ graphite_server_dns +'/metrics/find/'

   params = {
      'query':prefix_from + '.*'
   }


   resp = requests.get(url=url, params=params)
   data = json.loads(resp.content)

   #print data

   count_nodes = len(data)

   print "nodes loaded - count nodes: ", count_nodes
   #print data[1]['id']
   #print data[1]['expandable']


   i1 = 0
   arr_nodes = []
   data_by_timestamp = {}
   for lp_node in data:
      lp_srv  = lp_node['id']
      lp_text = lp_node['text']
      lp_allow_children = lp_node['allowChildren']
      #print "found node " + lp_srv + ' ' +  lp_text + ' - ' + str(lp_allow_children)
      print "found node " +  ' ' +  lp_text 
      arr_nodes.append( lp_text )


   return  arr_nodes





def  duplicate_one_day():

   # primitive implementation - reading from local file system
   '''
   ceresdir_servers = '/opt/graphite/storage/ceres/servers'
   for lpdir in os.listdir( ceresdir_servers ):
       if os.path.isdir(os.path.join(ceresdir_servers,lpdir)):
         migrate_one_server(lpdir)
   '''


   # new implementation - getting nodes from API
   i2=0
   for lpdir in nodes_under_prefix:
      i2+=1
      print "\nserver", lpdir
      migrate_one_server(lpdir)
      print "sleep ..."
      time.sleep( sleep_seconds )
      if i2 > it_max_hosts:
         break
   return




# init stuff
graphite_server_dns = sys.argv[1]

arg_day_start  = datetime.strptime( sys.argv[2] , "%Y-%m-%d")

days_forward = 1
if int(sys.argv[3]) > 1 :
   days_forward =  int(sys.argv[3])

nodes_under_prefix = get_nodes_under_prefix_from()

arg_day_end    = arg_day_start + timedelta(days_forward)
print "duplicate total from " , str(arg_day_start)[0:10], str(arg_day_end)[0:10]

# Splitting the date range into single days - 
# Iterating over each day
delta_increment = (arg_day_end - arg_day_start) / days_forward
for i in range(days_forward):
   lp_date = arg_day_start + i*delta_increment
   str_day_start = "00:00_" + lp_date.strftime("%Y%m%d" )
   str_day_end   = "23:59_" + lp_date.strftime("%Y%m%d" )
   print "    duplicate loop from " + str_day_start + "  " +str_day_end
   duplicate_one_day()


exit(0)