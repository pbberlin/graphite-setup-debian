#!/bin/bash
#

### BEGIN INIT INFO
# Provides:          graphite writers
# Required-Start:    xxx
# Required-Stop:     xxx
# Should-Start:      $named
# Default-Start:     2 3 4 5
# Default-Stop:      
# Short-Description: graphite relay and writers
# Description:       graphite relay and writers
#                    row2
#                    row3
### END INIT INFO

# /etc/init.d/rsync: start and stop graphite relay and writers


APPNAME="graphite relay and writers"
GRAPHITE_ROOT=/opt/graphite

. /lib/lsb/init-functions



if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


#writer_pids=` ps aux | grep 'uwsgi\|nginx\|python'  | grep  -v "rollup"  |  grep  -v "grep"  | grep   "writer\|relay" | pgrep -f "carbon-daemon.py"  `
 writer_pids=` ps aux | grep 'uwsgi\|nginx\|python'  | grep  -v "rollup"  |  grep  -v "grep"  | grep   "writer"        | pgrep -f "carbon-daemon.py"  `



start() {
    initlog -c "echo -n Starting $APPNAME... "
    #/path/to/FOO &
    # touch /var/lock/subsys/FOO
    success $"$APPNAME started"
    echo
}

stop() {
    initlog -c "echo -n Stopping $APPNAME... "
    #killproc FOO
    #rm -f /var/lock/subsys/FOO
    echo
}

status() {
    echo "writer pids are $writer_pids " 1>&2
}

### main logic ###
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        status
        ;;
  restart|reload)
        stop
        start
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|reload}"
        exit 1
esac
exit 0