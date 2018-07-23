#!/bin/sh
function hf_sync(){
    rm -rf /dev/shm/run /dev/shm/rom.z /dev/shm/rom.z.md5sum /dev/shm/build
    rsync -a --include=\"*/\" --include=\"*.py\" --include=\"*.sh\" --exclude=\"*\" . /dev/shm/build
}
function hf_clean(){
    rm -rf /dev/shm/build/mkupdatep.sh /dev/shm/build/data* /dev/shm/build/.git /dev/shm/build/ext/can /dev/shm/build/ext/hello_world /dev/shm/build/ext/rs485 /dev/shm/build/hf-viewer
    cd /dev/shm/
}
function hf_clean_bin(){
    rm -rf /dev/shm/build/ /dev/shm/run /dev/shm/boot_run.sh
}
function hf_build(){
    cd /dev/shm/build
    source buildhf.sh
}
function hf_sync_bin(){
    cd /dev/shm/build
    #find -iname "*.py" -exec rm {} \;
    #find -iname "*.pyc" -exec rm {} \;
    #find -iname "*.c" -exec rm {} \;
    #rm -rf /dev/shm/build/hf.conf /dev/shm/build/boot_run.sh /dev/shm/build/buildhf.sh
    rsync -a --include="*/" --include="*.so" --exclude="*" /dev/shm/build/ /dev/shm/run
    #rsync -a /dev/shm/build /dev/shm/run
    cp /dev/shm/build/boot_run.sh /dev/shm/
    cd /dev/shm
}
function mkpackage(){
    target_dir=$1
    felow_install_shell_command_file=$2
    echo "tar $target_dir" 
    tar --exclude="*.log" --exclude="*.c" --exclude="*.py"  --exclude="data/*" -zcf - $target_dir | base64 >/dev/shm/._base64
    printf "test_base64=\"">rom.z
    while IFS='' read -r line || [[ -n "$line" ]]; do
    printf "$line\\" >>rom.z
    printf "n" >>rom.z
    done </dev/shm/._base64
    rm /dev/shm/._base64
	#rm /dev/shm/mkupdatep.sh
	#rm /dev/shm/run/buildhf.sh
	
    echo "\"" >>rom.z
    echo 'cd /home/pi/hf_formation/'>>rom.z
    echo 'printf $test_base64|base64 -d|tar zxf -'>>rom.z
    if [[ -e $fellow_install_shell_command_file ]]; then
        cat $fellow_install_shell_command_file >>rom.z
    fi
	
    chmod +x rom.z
    m=$(md5sum /dev/shm/rom.z)
    echo $m > /dev/shm/rom.z.md5sum
    echo $m
}
function hf_cp(){
    cp /dev/shm/rom.* ~/hf_formation/run/data/
}
function usage(){
   echo "usage:"
   echo "    $1 test_dir [the_command.sh]"
}
if [[ $# != 0 ]]
then
    #hf_sync
    #hf_clean
    #hf_build
    #hf_sync_bin
    mkpackage $1 $2
    #hf_clean_bin
    #hf_cp
else
   usage $0
fi
