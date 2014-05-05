#!/bin/bash
# Make sure only www-data can run our script
_user="$(id -u -n)"
if [ "$_user" != "www-data" ]; then
   echo "This script must be run as www-data" 1>&2
   exit 1
fi



export GRAPHITE_ROOT=/opt/graphite
export LOGDAY=$(date +"%F")

ulimit -n 65536


rm $GRAPHITE_ROOT/storage/log/rollup-test.err
find $GRAPHITE_ROOT/storage/log -iname 'rollup-*.log'  -mtime +10   -type f  -delete
find $GRAPHITE_ROOT/storage/log -iname '*.log.*'       -mtime +10   -type f  -delete


if ps -ef | grep -v grep | grep "$GRAPHITE_ROOT/bin/ceres-maintenance" ; then
  echo "rollup still running " 
  exit 0
else
  $GRAPHITE_ROOT/bin/ceres-maintenance   --verbose   --daemon  --configdir=$GRAPHITE_ROOT/conf/carbon-daemons/writer-1/   --root=$GRAPHITE_ROOT/storage/ceres  --log=$GRAPHITE_ROOT/storage/log/rollup-$LOGDAY.log     rollup
  echo "started successfully" 
fi