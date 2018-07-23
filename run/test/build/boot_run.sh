#!/bin/sh

LIUGH=`screen -ls`
RESULT=`echo $LIUGH |grep -c "web"`

if [ $RESULT -gt 0 ]; 
  then 

  echo "HF SYS is running"
  exit; 
fi

echo "running HF SYS...."

cd ~/hf_formation/run
screen -dmS net ~/hf_formation/run_setnetwork.sh
screen -dmS web ~/hf_formation/run_webserver.sh
screen -dmS con ~/hf_formation/run/hf-main.py
