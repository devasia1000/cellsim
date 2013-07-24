#!/usr/bin/python
 
""" 
Glen Gibb, February 2011

modified by Devasia Manuel for MIT's Alfalfa project
"""

from mininet.topo import Topo 
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.node import Node
from mininet.topolib import TreeNet
from mininet.util import quietRun
from mininet.net import Mininet

import sys
from time import sleep
 
#################################

def startNAT( root, inetIntf='eth0', subnet='10.0/8' ):
    """Start NAT/forwarding between Mininet and external network
    root: node to access iptables from
    inetIntf: interface for internet access
    subnet: Mininet subnet (default 10.0/8)="""
 
    # Identify the interface connecting to the mininet network
    localIntf =  root.defaultIntf()
 
    # Flush any currently active rules
    root.cmd( 'iptables -F' )
    root.cmd( 'iptables -t nat -F' )
 
    # Create default entries for unmatched traffic
    root.cmd( 'iptables -P INPUT ACCEPT' )
    root.cmd( 'iptables -P OUTPUT ACCEPT' )
    root.cmd( 'iptables -P FORWARD DROP' )
 
    # Configure NAT
    root.cmd( 'iptables -I FORWARD -i', localIntf, '-d', subnet, '-j DROP' )
    root.cmd( 'iptables -A FORWARD -i', localIntf, '-s', subnet, '-j ACCEPT' )
    root.cmd( 'iptables -A FORWARD -i', inetIntf, '-d', subnet, '-j ACCEPT' )
    root.cmd( 'iptables -t nat -A POSTROUTING -o ', inetIntf, '-j MASQUERADE' )
 
    # Instruct the kernel to perform forwarding
    root.cmd( 'sysctl net.ipv4.ip_forward=1' )
 
def stopNAT( root ):
    """Stop NAT/forwarding between Mininet and external network"""
    # Flush any currently active rules
    root.cmd( 'iptables -F' )
    root.cmd( 'iptables -t nat -F' )
 
    # Instruct the kernel to stop forwarding
    root.cmd( 'sysctl net.ipv4.ip_forward=0' )
 
def fixNetworkManager( root, intf ):
    """Prevent network-manager from messing with our interface,
       by specifying manual configuration in /etc/network/interfaces
       root: a node in the root namespace (for running commands)
       intf: interface name"""
    cfile = '/etc/network/interfaces'
    line = '\niface %s inet manual\n' % intf
    config = open( cfile ).read()
    if ( line ) not in config:
        print '*** Adding', line.strip(), 'to', cfile
        with open( cfile, 'a' ) as f:
            f.write( line )
    # Probably need to restart network-manager to be safe -
    # hopefully this won't disconnect you
    root.cmd( 'service network-manager restart' )
 
def connectToInternet( network, switch='s1', rootip='10.254', subnet='10.0/8'):
    """Connect the network to the internet
       switch: switch to connect to root namespace
       rootip: address for interface in root namespace
       subnet: Mininet subnet"""
    switch = network.get( switch )
    prefixLen = subnet.split( '/' )[ 1 ]
    routes = [ subnet ]  # host networks to route to
 
    # Create a node in root namespace
    root = Node( 'root', inNamespace=False )
 
    # Prevent network-manager from interfering with our interface
    fixNetworkManager( root, 'root-eth0' )
 
    # Create link between root NS and switch
    link = network.addLink( root, switch )
    link.intf1.setIP( rootip, prefixLen )
 
    # Start network that now includes link to root namespace
    network.start()
 
    # Start NAT and establish forwarding
    startNAT( root )
  
    # Establish routes from end hosts
    for host in network.hosts:
        host.cmd( 'ip route flush root 0/0' )
        host.cmd( 'route add -net', subnet, 'dev', host.defaultIntf() )
        host.cmd( 'route add default gw', rootip )
 
    return root

def setupRoutes(network):
        
    for host in network.hosts:
	if host.name is "cellsim":	    
	    host.cmd("sudo ifconfig cellsim-eth1 10.0.0.5 up")
	    # delete old routes
            #host.cmd("sudo route del -net 0.0.0.0 netmask 0.0.0.0 cellsim-eth0")
            #host.cmd("sudo route del -net 10.0.0.0 netmask 255.0.0.0 cellsim-eth0")
	    # create new routes
	    #host.cmd("sudo route add 10.0.0.2 cellsim-eth1")
	    #host.cmd("sudo route add 10.0.0.3 cellsim-eth0")
	    
def startCellsimAndApache(network, username, uplink, downlink, lossRate):	

    # find the client's MAC address and pass it to cellsimi
    clientMAC="";
    for host in network.hosts:
	if host.name is "client":
	    # mininet's MAC() is buggy, we're going to parse the MAC address from ifconfig
	    clientMAC=host.cmd("ifconfig client-eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}'")	   
	    clientMAC=clientMAC.replace("\n", "") 

    for host in network.hosts:
        if host.name is "cellsim":
	    # start cellsim
            host.sendCmd("nohup ./cellsim "+uplink+" "+downlink+" "+clientMAC+" "+lossRate+" >/tmp/cellsim-stdout 2>/tmp/cellsim-stderr &")
	    host.waitOutput()
	elif host.name is "server":
	    # start apache on server
	    host.cmd("service apache2 restart")


def startChromium(network, username, videolink):

    for host in network.hosts:
	if host.name is "client":
	    #start chromium
	    host.cmdPrint("su -c '~/Desktop/src/start_test.pl "+videolink+"' - "+username)


# Custom topology class
class MyTopo( Topo ):
    "cellsim"

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        server = self.addHost( 'server' )
        cellsim = self.addHost( 'cellsim' )
        client = self.addHost( 'client' )

        serverSwitch=self.addSwitch('s1')
        clientSwitch=self.addSwitch('s2')

        # Add links
        self.addLink( server, serverSwitch )
        self.addLink( cellsim, serverSwitch)
        self.addLink( client, clientSwitch )
        self.addLink( cellsim, clientSwitch)
	

topos = { 'cellsim': ( lambda: MyTopo() ) }

def CellsimNet ( **kwargs ):
    "Convenience function for returning cellsim topo"
    topo = MyTopo()
    return Mininet( topo, **kwargs )

if __name__ == '__main__':
    lg.setLogLevel( 'info')   
    
    # get arguments    
    arguments=sys.argv
    if len(arguments)!=6:
	print "Usage: <username> <uplinkTraceFile> <downlinkTraceFile> <lossRate> <youtubeVideoLink>"
	sys.exit(0)

    username=arguments[1]
    uplink=arguments[2]
    downlink=arguments[3]
    lossrate=arguments[4]
    videolink=arguments[5]

    #use own topo with mininet
    net = CellsimNet()
    net.startTerms()
    # Configure and start NATted connectivity
    rootnode = connectToInternet( net )
    
    print "*** Hosts are running and should have internet connectivity"
    print "*** Type 'exit' or control-D to shut down network"

    # setup routes for cellsim
    setupRoutes(net)
    # start cellsim
    startCellsimAndApache(net, username, uplink, downlink, lossrate)
    sleep(3)
    #start chromium
    startChromium(net, username, videolink)

    CLI( net )
    # Shut down NAT
    stopNAT( rootnode )
    net.stop()
