#!/usr/bin/env python3
from setuptools import setup

def main():
	setup(
		name="hostinator",
		version="1.0.0",
		description="Hostinator is a tool for automatically adding Docker containers to the hosts file.",
		url="https://gitlab.com/chrisgavin/hostinator",
		packages=["hostinator"],
		classifiers=[
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.2",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: 3.6",
		],
		install_requires=[
			"docker",
		],
		entry_points={
			"console_scripts":[
				"hostinator = hostinator.__main__:main",
			],
		},
	)

if __name__ == "__main__":
	main()
