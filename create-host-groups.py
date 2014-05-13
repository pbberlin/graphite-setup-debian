#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import _mysql
import sys
import getpass


if getpass.getuser() != "www-data" :
  print "this script must be run as www-data"
  sys.exit(1)


msg='''
This script is only an early prototype to demonstrate the ideas.
'''



ceres_dir = '/opt/graphite/storage/ceres/'
by_role_dir = 'roles/'


# helper to execute any sql select query
# the result is put into a dictionary with
# the first column of the resultset as the key.
# It is extremely simple and does not handle lots of possible complications
def execute_query(arg_host, arg_query):

    resDict = {}
    con = None

    try:
        con = mdb.connect(  host=arg_host, user='idealo', passwd='s3cr3t', connect_timeout=2 );
    
        with con: 
            cur = con.cursor()
            cur.execute(arg_query)
            rows = cur.fetchall()
            for row in rows:
                #print row
                arr_col = [s for s in row ]
                #resDict[ row[0]  ]  = [row[0],row[1], row[2]  ]
                resDict[ row[0]  ]  = arr_col
            #print "end of query %s" % arg_query


    except _mysql.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        
        #sys.exit(1)


    finally:
        if con:
            con.close()

    return resDict
            

# this query retrieves all foreman roles with hosts
q2 = '''
SELECT 
   t1.name   Hostname
 , t7.value  PureName
 , t2.name   Domain
 , t3.value  Rolle
 , t1.ip     IPadresse
FROM                                    foreman.hosts   t1
LEFT  JOIN              foreman.domains      t2  ON t1.domain_id = t2.id
LEFT  JOIN              foreman.fact_values  t3  ON t1.id        = t3.host_id   AND t3.fact_name_id=48 
LEFT  JOIN 		foreman.fact_values  t7  ON t1.id	 = t7.host_id   AND t7.fact_name_id=14 
WHERE      1=1
       AND NOT (t3.value  LIKE '%undef%')
/*       AND NOT (t3.value  =    'onekvmhost')  */
       AND NOT (t2.name   =    'lvl.bln')

       OR
       (
               t3.value IN ('mysql','mysqld','idealo_mongodb')

       )
ORDER BY t2.name, t3.value

'''


q3 = "select now()"

# this query detects whether a mysql machine is acting as slave
q4 = "select variable_value from information_schema.global_status where variable_name = 'Slave_running'";


res = execute_query('mysql-db1.ipx', q2)

print str( res )[:30] + " ... " + str( res)[-30:]



distinct_roles = {}
refined_host_groups = {}
for k in res.keys():
    lp_arr = res[k]
    # some special processing for role mysql
    if lp_arr[3] == 'mysql'  or lp_arr[3] == 'mysqld':
      #print lp_arr[1]
      res_slave = execute_query(  lp_arr[0], q4)
      #print str( res_slave[0]  )
      slaveRunning = 'OFF'
      for k1 in res_slave.keys():
        slaveRunning = k1
        #print k1,res_slave[k1], slaveRunning
      if slaveRunning == "ON" :
        lp_arr[3] = 'mysql_' + 'slave'
      else:
        lp_arr[3] = 'mysql_' + 'master'
        
      print lp_arr[1] , lp_arr[2], lp_arr[3]
    distinct_roles[ lp_arr[3]  ] = lp_arr[3]

    refined_host_groups[ lp_arr[1]  ]  =   lp_arr[3]    




# now the graphite part
# we write symlinks into directories
# this way we can put all hosts into any number of 
# other grouping directories


import subprocess
import os.path


print " "
print " creating parent dirs for symlinks if not exist "
if not os.path.exists(  ceres_dir  + by_role_dir ):
  os.makedirs( ceres_dir + by_role_dir )
for k2 in distinct_roles.keys():
  lp_dir = distinct_roles[k2]
  if not os.path.exists(  ceres_dir  + by_role_dir  + lp_dir ):
    os.makedirs( ceres_dir + by_role_dir + lp_dir )
    print "created dir " + lp_dir




print " " 
print " delete previous symlinks "
# this may take a while - alternatively we could search for symlinks only in the by_role_dir directory
counter_dirs = 0
for root, subdirs, files in os.walk( ceres_dir , followlinks=True ):
  for subdir in subdirs:
    dir_name = os.path.join(root, subdir)
    counter_dirs+=1
    #is_symlink =  os.path.islink( os.path.basename(dir_name) )
    is_symlink =  os.path.islink( dir_name )
    if counter_dirs % 10000 == 0:
      print "traversing dir number " +  str(counter_dirs) + " -  " + dir_name 
      #print files
    if is_symlink :
      print "  found symlink: " + dir_name + " - will delete it"
      bashCommand = "rm " + dir_name 
      process    = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output     = process.communicate()[0]
      print output




print " " 
print " create new symlinks "
for lp_host in refined_host_groups.keys():
  lp_role_dir = refined_host_groups[lp_host]
  print lp_host , lp_role_dir
  if(         not os.path.isfile(  ceres_dir  + by_role_dir  + lp_role_dir  +lp_host    ) 
        and       os.path.isdir( ceres_dir + 'servers/' + lp_host  )   
  ):
    print "created symlink " +  ceres_dir + 'servers/' + lp_host + "  =>  " +  ceres_dir + by_role_dir +  lp_role_dir   + '/' + lp_host
    os.symlink(  ceres_dir + 'servers/' + lp_host  ,  ceres_dir + by_role_dir +  lp_role_dir  + '/' + lp_host  ) 
    #break


