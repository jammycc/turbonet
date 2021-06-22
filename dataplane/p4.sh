#!/bin/bash

P4_NAME=turbonet

CUR_DIR=`pwd`
P4_BUILD=${SDE}/pkgsrc/p4-build/
DATAPLANE_DIR=$(cd "$(dirname "$0")";pwd)
P4_PATH=${DATAPLANE_DIR}/p4src/main.p4

Help () {
    echo "p4.sh configure    --- Start TurboNet"
    echo "p4.sh compile      --- Stop TurboNet"
    echo "p4.sh run          --- Install TurboNet"
}

if [[ -n "$1" ]]
then
    if [[ "$1" = "configure" ]] 
    then
        cd $P4_BUILD
        echo $P4_PATH
        ./configure --prefix=${SDE_INSTALL} --with-tofino enable_thrift=yes P4_NAME=${P4_NAME} P4_PATH=${P4_PATH}
        cd $CUR_DIR
    elif [[ "$1" = "compile" ]] 
    then
        # python gen_p4_code.py
        cd $P4_BUILD
        make -j16
        make install
        cd $CUR_DIR
    
    elif [[ "$1" = "start" ]] 
    then
        cd $FC_DIR
        tmux new -d -s switchd "$SDE/run_switchd.sh -p turbonet -c ${P4_DIR}/turbonet.conf"
        sleep 20
        cd $CP_DIR
        tmux new -d -s turbonet "python manage.py runserver 0.0.0.0:8080"
        cd $CUR_DIR
    elif [[ "$1" = "deploy" ]] 
    then
        cd $P4_DIR
        make configure-tofio
        make
        cd $CUR_DIR
    elif [[ "$1" = "stop" ]] 
    then
        tmux kill-session -t turbonet
        tmux kill-session -t switchd
    else
        Help
    fi
else 
    Help
fi
