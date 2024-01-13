#!/bin/bash
set auexo -pipefail

# This is the script to install Tailscale on the Phidgets SBC4 computer, which is an armhf and ships with Debian Bullseye

# 1. Add Tailscale's GPG key
mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkgs.tailscale.com/stable/debian/bullseye.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null

# 2. Add the tailscale repository
curl -fsSL https://pkgs.tailscale.com/stable/debian/bullseye.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list

# 3. Install Tailscale
apt-get update && apt-get install tailscale

# 4. Start Tailscale!
tailscale up
