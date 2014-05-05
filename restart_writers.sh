#!/bin/bash
# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


export GRAPHITE_ROOT=/opt/graphite

#writer_pids=` ps aux | grep 'uwsgi\|nginx\|python'  | grep  -v "rollup"  |  grep  -v "grep"  | grep   "writer\|relay" | pgrep -f "carbon-daemon.py"  `
 writer_pids=` ps aux | grep 'uwsgi\|nginx\|python'  | grep  -v "rollup"  |  grep  -v "grep"  | grep   "writer"         | pgrep -f "carbon-daemon.py"  `
echo "writer pids are $writer_pids " 1>&2


echo " ...give the writers a chance to stop manually, and write their cache to disk"
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-1  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-2  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-3  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-4  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-5  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-6  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-7  stop
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-8  stop
echo " ...sleeping 10 secs - while relay is caching "
sleep 10


echo " ...now hard crashing the writers"
kill -9  $writer_pids
sleep 1
ulimit -n 65536
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-1  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-2  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-3  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-4  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-5  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-6  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-7  start
$GRAPHITE_ROOT/bin/carbon-daemon.py writer-8  start



sleep 2
echo " ...restart relay"
$GRAPHITE_ROOT/bin/carbon-daemon.py relay     stop
sleep 1
$GRAPHITE_ROOT/bin/carbon-daemon.py relay     start


chown       www-data.www-data  /opt/graphite/storage/*.pid
chown   -R  www-data.www-data  /opt/graphite/storage/log/