#!/usr/bin/python3
import os
import sys
import subprocess

DEBUG = False

ELEMENTS = (
    "ACTION",
    "SUBSYSTEM",
    "BUSNUM",
    "DEVNUM",
    "DEVPATH",
    "ID_MODEL",
    "ID_MODEL_FROM_DATABASE",
)

###################### TEST Event ########################

TEST = {
    "ACTION": "add",
    "SUBSYSTEM": "usb",
    "BUSNUM": "5",
    "DEVNUM": "4",
    "DEVPATH": "/devices/pci0000:00/0000:00:1d.0/0000:04:00.0/0000:05:01.0/0000:07:00.0/0000:08:00.0/0000:09:00.0/usb7",
    "ID_MODEL": "none",
    "ID_MODEL_FROM_DATABASE": "none",
}


def __dbg(msg):
    global DEBUG
    if DEBUG:
        print(msg, file=sys.stderr)


def __validate(event):

    for key in event.keys():

        if event[key] == "":
            print("Unsupported " + key + ": " + event[key])
            sys.exit(2)

        if event[key] != "usb" and key == "SUBSYSTEM":
            __dbg("don't care about " + key + ": " + event[key])
            sys.exit(0)

        if "hub" in event[key].lower():
            __dbg("don't care about USB hubs: " + devpath)
            sys.exit(0)

    return True


def get_event():

    event = {}

    for e in ELEMENTS:

        if DEBUG:
            event[e] = TEST[e] or ""
        else:
            event[e] = os.getenv(e) or ""

        if event["ACTION"] == "":

            event["ACTION"] = "add"
            event["SUBSYSTEM"] = "usb"

    if __validate(event=event):
        return event


def process_domain(domain: dict, event: dict):

    if domain["name"] == "":
        __dbg("udev event doesn't match any device in config")
        sys.exit(0)

    for port in domain["ports"]:

        if port["BUSNUM"] == event["BUSNUM"]:

            if "DEVNUM" not in port.keys():

                return {
                    "domain": domain["name"],
                    "action": event["ACTION"],
                    "device": {
                        "BUSNUM": event["BUSNUM"],
                        "DEVNUM": event["DEVNUM"],
                        "DEVPATH": event["DEVPATH"],
                    },
                }

            elif port["DEVNUM"] == event["DEVNUM"]:

                return {
                    "domain": domain["name"],
                    "action": event["ACTION"],
                    "device": {
                        "BUSNUM": event["BUSNUM"],
                        "DEVNUM": event["DEVNUM"],
                        "DEVPATH": event["DEVPATH"],
                    },
                }


def process_devices(action: str, domain: str, device: dict):

    if action == "add":
        __dbg("attaching device")
        op = "attach-device"
    elif action == "remove":
        __dbg("detaching device")
        op = "detach-device"
    else:
        __dbg("Unsupported ACTION: " + action)

    __dbg("busnum={} devnum={}".format(device["BUSNUM"], device["DEVNUM"]))

    device_xml = '<hostdev mode="subsystem" type="usb"><source><address bus="{}" device="{}"/></source></hostdev>'
    device_xml = device_xml.format(device["BUSNUM"], device["DEVNUM"])

    print(["/usr/bin/virsh", op, domain, "/dev/stdin"])

    virsh = subprocess.Popen(
        ["/usr/bin/virsh", op, domain, "/dev/stdin"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
    )
    virsh.communicate(input=device_xml.encode("ascii"))
    virsh.wait()
