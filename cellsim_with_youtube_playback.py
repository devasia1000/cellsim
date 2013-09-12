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
from os.path import expanduser
 
#################################

def setupRoutes(network):
        
    for host in network.hosts:
	if host.name is "cellsim":	    
	    host.cmd("sudo ifconfig cellsim-eth1 10.0.0.5 up")
	   
 
def startCellsimAndYouTubePlayback(network, username, uplink, downlink, lossRate):	

    # find the client's MAC address and pass it to cellsimi
    clientMAC="";
    for host in network.hosts:
	if host.name is "client":
	    # mininet's MAC() is buggy, we're going to parse the MAC address from ifconfig
	    clientMAC=host.cmd("ifconfig client-eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}'")	   
	    clientMAC=clientMAC.replace("\n", "")
            host.cmd("sudo service dnsmasq restart")
	    host.cmd("sudo /etc/init.d/nscd restart")

    for host in network.hosts:
        if host.name is "cellsim":
	    # start cellsim
            host.sendCmd("nohup ./cellsim "+uplink+" "+downlink+" "+clientMAC+" "+lossRate+" >/tmp/cellsim-stdout 2>/tmp/cellsim-stderr &")
	    host.waitOutput()

	elif host.name is "server":
	    #start youtube_playback on server
		host.cmd("nohup javac "+expanduser("~")+"/youtube_playback/*.java >/tmp/youtube_playback-stdout 2>/tmp/youtube_playback-stderr &");	   	
		host.cmd("nohup sudo java "+expanduser("~")+"/youtube_playback/Main >/tmp/youtube_playback-stdout 2>/tmp/youtube_playback-stderr &");


def startChromium(network, username, videolink):

    for host in network.hosts:
	if host.name is "client":
	    #start chromium
	    host.cmdPrint("su -c '"+expanduser("~")+"/src/start_test.pl "+videolink+"' - "+username)


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
    net.start()
    net.startTerms()
    
    print "*** Hosts are running"
    print "*** Type 'exit' or control-D to shut down network"
    # setup routes for cellsim
    setupRoutes(net)
    # start cellsim
    startCellsimAndYouTubePlayback(net, username, uplink, downlink, lossrate)
    sleep(5)
    #start chromium
    startChromium(net, username, videolink)

    CLI( net )
    # Shut down NAT
    #stopNAT( rootnode )
    net.stop()
