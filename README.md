# Hostinator
Hostinator is a tool for automatically adding Docker containers to the hosts file.

## Purpose
Docker Compose has a really useful feature that enables you to access a container by alias from within containers on the same network. The primary aim of this project is to make those same resolutions work from the Docker host.

## Features
* Detects new Docker containers dynamically by monitoring the Docker socket for events.
* Puts your hosts file back to how it was originally on exit.
