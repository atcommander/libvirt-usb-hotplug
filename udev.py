#!/usr/bin/python3

import libvirt
import config


def main():

    libvirt.DEBUG = True

    event = libvirt.get_event()

    for domain in config.CONFIG:
        device = libvirt.process_domain(domain=domain, event=event)
        libvirt.process_devices(
            action=device["action"], domain=device["domain"], device=device["device"]
        )

    print(event)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
