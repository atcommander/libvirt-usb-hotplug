#!/usr/bin/python3

import libvirt
import config


def main():

    for domain in config.CONFIG:
        for port in domain["ports"]:

            libvirt.process_devices(action="add", domain=domain["name"], device=port)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
