#!/usr/bin/python3

import os
import sys
import subprocess

##################### CONFIG #######################

config = [
    (
        "win10",
        [
            "/devices/pci0000:00/0000:00:1d.0/0000:04:00.0/0000:05:01.0/0000:07:00.0/0000:08:02.0/0000:0b:00.0/usb7",
            "/devices/pci0000:00/0000:00:1d.0/0000:04:00.0/0000:05:01.0/0000:07:00.0/0000:08:00.0/0000:09:00.0/usb5",
        ],
    ),
]

debug = True

###################### CODE ########################


def dbg(msg):
    global debug
    if debug:
        print(msg, file=sys.stderr)


# identify action and actual device added

dbg("--- BEGIN ---")
print(os.getenv())
action = os.getenv("ACTION") or ""
if action == "":
    print("Unsupported ACTION: " + action)
    sys.exit(2)

subsystem = os.getenv("SUBSYSTEM") or ""
if subsystem != "usb":
    dbg("don't care about SUBSYSTEM: " + subsystem)
    sys.exit(0)

busnum = os.getenv("BUSNUM") or ""
if busnum == "":
    dbg("don't care about BUSNUM: " + busnum)
    sys.exit(0)
busnum = int(busnum)

devnum = os.getenv("DEVNUM") or ""
if devnum == "":
    dbg("don't care about DEVNUM: " + devnum)
    sys.exit(0)
devnum = int(devnum)

devpath = os.getenv("DEVPATH") or ""
if devpath == "":
    dbg("don't care about DEVPATH: " + devpath)
    sys.exit(0)
devpath = os.path.realpath(devpath)

hub_search = ["ID_MODEL", "ID_MODEL_FROM_DATABASE"]
for s in hub_search:
    if "hub" in (os.getenv(s) or "").lower():
        dbg("don't care about USB hubs: " + devpath)
        sys.exit(0)

# find domain for current device

found_domain = ""

for domain, ports in config:
    for port in ports:
        print(port)
        if port != devpath and (port + "/") not in devpath:
            continue
        # If device path does match, but there are sub devices available
        # ignore this device (don't pass through a USB hub itself, causes problems)
        found_domain = domain
        break

    if found_domain != "":
        break

if found_domain == "":
    dbg("udev event doesn't match any device in config")
    sys.exit(0)

# tell libvirt to attach/detach device

if action == "add":
    dbg("attaching device")
    op = "attach-device"
elif action == "remove":
    dbg("detaching device")
    op = "detach-device"
else:
    dbg("Unsupported ACTION: " + action)

dbg("busnum={} devnum={} devpath={}".format(busnum, devnum, devpath))


device_xml = '<hostdev mode="subsystem" type="usb"><source><address bus="{}" device="{}"/></source></hostdev>'
device_xml = device_xml.format(busnum, devnum)

virsh = subprocess.Popen(
    ["virsh", op, found_domain, "/dev/stdin"],
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
)
virsh.communicate(input=device_xml.encode("ascii"))
virsh.wait()

dbg("---  END ---")
