$file=`cat verizon3g-downlink.rx`;
@lines=split("\n", $file);
$counter=0;

foreach (@lines){
 $line=$_;
 $line =~ s/\D//g;
   
 if($counter==0){
  $reference=$line;
 } else {
  $num=$line-$reference;
  print int($num/10000000), "\n";
 }

 $counter=$counter+1;
}
