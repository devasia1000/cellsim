print `make`;

#./cellsim <up> <down> <client_mac> <loss_rate>
print "Enter Client MAC:\n";
$mac=<STDIN>;
chomp($mac);
print `./cellsim sprint-uplink_processed.txt sprint-downlink_processed.txt ${mac} 0.1`;
