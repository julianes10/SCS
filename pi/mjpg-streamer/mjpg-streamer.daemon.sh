#!/bin/bash
# Original file copied from https://community.octoprint.org/t/setting-up-octoprint-on-a-raspberry-pi-running-raspbian/2337

echo "Loading variables from config file $1"
source $1

# runs MJPG Streamer, using the provided input plugin + configuration
function runMjpgStreamer {
    pushd $MJPGSTREAMER_HOME
    LD_LIBRARY_PATH=. ./mjpg_streamer -i "$MJPGSTREAMER_INPUT"  -o "$MJPGSTREAMER_OUTPUT"
    popd
}

runMjpgStreamer

