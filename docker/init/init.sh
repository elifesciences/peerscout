#!/bin/sh

set -e

# elife user id
USER_ID=1000
echo 'changing ownership to $USER_ID, and...'

echo 'copying aws credentials...'

cp -r /home/elife/user-config-aws/* /home/elife/volume-config-aws
chown -R $USER_ID:$USER_ID /home/elife/volume-config-aws

echo 'done'
