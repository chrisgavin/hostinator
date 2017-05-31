# Hostinator
Hostinator is a tool for automatically adding Docker containers to the hosts file.

## Purpose
Docker Compose has a really useful feature that enables you to access a container by alias from within containers on the same network. The primary aim of this project is to make those same resolutions work from the Docker host.

## Features
* Detects new Docker containers dynamically by monitoring the Docker socket for events.
* Puts your hosts file back to how it was originally on exit.

## Docker Image
This project is availiable as a Docker image at [`chrisgavin/hostinator`](https://hub.docker.com/r/chrisgavin/hostinator/). You can use it like so:

```sh
docker run -it --rm \
	-v "/var/run/docker.sock:/var/run/docker.sock" \
	-v "/etc/:/mnt/etc/" \
	chrisgavin/hostinator
```

You can also integrate this with an existing Docker Compose configuration. You can add it as a service in your Docker Compose file.

```yaml
hostinator:
  image: "chrisgavin/hostinator"
  volumes:
    - "/var/run/docker.sock:/var/run/docker.sock"
    - "/etc/:/mnt/etc/"
```
