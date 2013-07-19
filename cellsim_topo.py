from mininet.topo import Topo

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
