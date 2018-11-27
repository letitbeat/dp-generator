#!/usr/bin/python

"""
This is the network topology generator script
which uses Containernet capabilities to enable
Docker containers act as hosts

"""
from mininet.net import Containernet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, error, setLogLevel

import pydot
import socket
import json
import urllib2
import subprocess
from argparse import ArgumentParser

setLogLevel('info')

TOPOLOGY_FILE = "topology.dot"
ANALYZER_URL  = "http://analyzer:5000/topology"
HOSTS_IMAGE   = "generator:latest"  # ubuntu:trusty or any other image could work

parser = ArgumentParser()
parser.add_argument("-a", "--analyzer",
                    action="store_true", dest="analyze", default=False,
                    help="The topology and sniffed packets should be sent to the analyzer")

args = parser.parse_args()

# Loads and parses the topology file in .dot format
# and returns a graph object which represents nodes and edges.
try:
    topology = open(TOPOLOGY_FILE, "r").read()
    graph = pydot.graph_from_dot_data(topology)[0]
except:
    error('There was a problem loading the topology file: {} \n'.format(TOPOLOGY_FILE))
    raise SystemExit

switches = []
hosts    = []
edges    = []

switchesMap = {}
hostsMap    = {}

bpfFilter = str(graph.get_target())

# If the attribute "group" is not set, the node is treated as host,
# otherwise, it should be either "hosts" or "switches"
for n in graph.get_nodes():
    if n.get_group() is None or n.get_group() == "hosts":
        hosts.append(n.get_name())
    elif n.get_group() == "switches":
        switches.append(n.get_name())

info('*** Creating network\n')

net = Containernet(controller=None)

info('*** Adding controller\n')

controller = socket.gethostbyname('onos')
net.addController(name='onos', controller=RemoteController, ip=controller, port=6633)

info('*** Adding docker containers\n')

hosts.sort()
i = 0
for h in hosts:
    host = net.addDocker(h, ip=net.getNextIp(), dimage=HOSTS_IMAGE, ports=[8800 + i],
                         port_bindings={6000: 8800 + i})
    hostsMap[h] = host
    i += 1

info('*** Adding switches\n')

for s in switches:
    switch = net.addSwitch(s)
    switchesMap[s] = switch

info('*** Creating links\n')
for e in graph.get_edges():
    n1 = hostsMap.get(e.get_source())
    isN1Switch = False
    if n1 is None:
        n1 = switchesMap.get(e.get_source())
        isN1Switch = True

    n2 = hostsMap.get(e.get_destination())
    isN2Switch = False
    if n2 is None:
        n2 = switchesMap.get(e.get_destination())
        isN2Switch = True

    nl = ""
    ports = str(e.get_label()).strip('"').split(" ") # "label" property from the edge definition will be parsed as ports
    p1 = int(ports[0])
    p2 = int(ports[1])
    if isN1Switch and isN2Switch:
        nl = net.addLink(n1, n2, port1=p1, port2=p2, cls=TCLink, delay='100ms', bw=1)
    else:
        nl = net.addLink(n1, n2, port1=p1, port2=p2)
    edges.append(nl)

if args.analyze:
    # Format the links data which is going to be sent to the analyzer
    links = []
    for l in edges:
        t = str(l).split("<->")
        n = t[0].split("-")[0]

        if switchesMap.get(n) is not None:
            links.append("{}:{}".format(t[1].split("-")[0], t[0]))
        links.append("{}:{}".format(n, t[1]))


    info('*** Sending topology to analyzer\n')

    data = {
        'links': links,
        'hosts': hosts,
        'switches': switches,
        'dot': topology
    }

    req = urllib2.Request(ANALYZER_URL)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))


info('*** Starting network\n')
net.start()

if args.analyze:
    info('*** Running sniffer for each switch interface\n')

    switchLinks = []
    for s in links:
        sl = str(s).split(":")[1]
        switchLinks.append(sl)

    cmd = "/containernet/sniffer -i {} -f {}".format(",".join(switchLinks), bpfFilter)
    subprocess.Popen(cmd, shell=True)

    info("*** Starting generators \n")
    # ips = []
    #
    # for h in hostsMap.values():
    #     ips.append(str(h.IP()))

    # Request from central analyzer
    for h in hostsMap.values():
        #    h.cmdPrint("nohup ./main & -p {} -dP {}".format(protocol, dstPort) ) #h.cmdPrint("./main -t {}".format(",".join(ips)))
        h.cmdPrint("nohup ./main &")


info('*** Running CLI\n')
CLI(net)

info('*** Stopping network\n')
net.stop()

info('*** Stopping sniffers\n')
subprocess.Popen("pkill sniffer", shell=True)
