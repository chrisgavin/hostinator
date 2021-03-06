#!/usr/bin/env python3
import os
import sys
import logging
import signal
from typing import Set, List, TextIO
import shutil
import hashlib
import docker

_LOG = logging.getLogger(__name__)
_DOCKER = docker.from_env()

# Config Variables
_HOSTINATOR_VERBOSITY = os.environ.get("HOSTINATOR_VERBOSITY", "INFO")
_HOSTINATOR_NETWORK = os.environ.get("HOSTINATOR_NETWORK", None)
_HOSTINATOR_HOSTS_DIR = os.environ.get("HOSTINATOR_HOSTS_DIR", "/etc/")

_MARKER = "Hostinator Managed Aliases" + (" (%s)" % _HOSTINATOR_NETWORK if _HOSTINATOR_NETWORK else "")
_START_MARKER = "# " + _MARKER
_END_MARKER = "# End " + _MARKER
_HOSTS_FILE = os.path.join(_HOSTINATOR_HOSTS_DIR, "hosts")
_SWAP_FILE = os.path.join(_HOSTINATOR_HOSTS_DIR, ".hosts.swp")

def get_host_line(ip: str, aliases: Set[str]) -> str:
	return "%s %s" % (ip, " ".join(aliases))

def get_container_hosts(container: docker.api.container.ContainerConfig) -> List[str]:
	lines = [] # type: List[str]
	# These are aliases that apply to the container rather than the network.
	# They can therefore only be assigned to one IP.
	container_specific_aliases = [container.attrs["Config"]["Hostname"], container.name]
	for network in container.attrs["NetworkSettings"]["Networks"].values():
		if _HOSTINATOR_NETWORK is not None:
			network_details = _DOCKER.networks.get(network["NetworkID"])
			if _HOSTINATOR_NETWORK != network_details.name:
				_LOG.debug("Ignoring host on network \"%s\" because it isn't \"%s\".", network_details.name, _HOSTINATOR_NETWORK)
				continue
		ip = network["IPAddress"]
		aliases = set(network["Aliases"] or [])
		aliases.update(container_specific_aliases)
		container_specific_aliases = []
		if aliases:
			lines += [get_host_line(ip, aliases)]
		else:
			_LOG.warning("Could not find any valid aliases for network %s on container %s.", network["NetworkID"][:10], container.short_id)
	return lines

def generate_hosts_file_snippet() -> List[str]:
	lines = [_START_MARKER]
	for container in _DOCKER.containers.list():
		lines += get_container_hosts(container)
	lines += [_END_MARKER]
	return lines

def remove_marked_lines(lines: List[str]) -> List[str]:
	result = [] # type: List[str]
	in_marked_area = False
	for line in lines:
		if not in_marked_area:
			if line == _START_MARKER:
				in_marked_area = True
			else:
				result += [line]
		else:
			if line == _END_MARKER:
				in_marked_area = False
	if in_marked_area:
		raise RuntimeError("The host file contained a start marker, but not an end marker.")
	return result

def update_hosts(append: List[str]) -> None:
	_LOG.info("Updating the hosts file.")
	# Load a copy of the hosts file.
	shutil.copy2(_HOSTS_FILE, _SWAP_FILE)
	with open(_SWAP_FILE) as swap_file:
		contents = swap_file.readlines()

	# The hosts file might have been mounted in from Windows or something weird like that. So we try and preserve the line endings.
	line_ending = "\n"
	if contents and len(contents[0]) > 1 and contents[0][-2:] == "\r\n":
		line_ending = "\r\n"
	# We don't want the line endings anymore.
	contents = [line.strip("\n\r") for line in contents]

	contents = remove_marked_lines(contents)

	contents += append
	with open(_SWAP_FILE, "w") as swap_file:
		for line in contents:
			swap_file.write(line)
			swap_file.write(line_ending)

	shutil.move(_SWAP_FILE, _HOSTS_FILE)
	_LOG.info("Hosts file updated.")

def sigterm_handler(*_):
	sys.exit(0)

def main() -> None:
	log_level = logging.getLevelName(_HOSTINATOR_VERBOSITY)
	logging.basicConfig(level=log_level)
	try:
		signal.signal(signal.SIGTERM, sigterm_handler)
		update_hosts(generate_hosts_file_snippet())
		for event in _DOCKER.events(decode=True):
			if event["Type"] == "container" and event["status"] in ["start", "die"]:
				update_hosts(generate_hosts_file_snippet())
	except KeyboardInterrupt:
		pass
	finally:
		update_hosts([])

if __name__ == "__main__":
	main()
