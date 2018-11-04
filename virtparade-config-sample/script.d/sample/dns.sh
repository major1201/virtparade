#!/bin/bash

set -e
set -x

mount_dir=$1
index=$2
dns=$3

if [ "${index}" == "0" ]; then
    echo "nameserver ${dns}" > "${mount_dir}/etc/resolv.conf"
else
    echo "nameserver ${dns}" >> "${mount_dir}/etc/resolv.conf"
fi
