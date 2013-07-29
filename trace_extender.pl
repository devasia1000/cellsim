@diffArray;
$i=0;

while($read1=<STDIN>){
 $read2=<STDIN>;
 #print $read2, " - ", $read1, "\n";
 $diff=$read2-$read1;
 #print $diff, "\n";
 $diffArray[$i]=$diff;
 $i=$i+1;
}

$value=1;
$j=0;
$length=scalar @diffArray;
@newArray;
#print $length;
while($j<$length){
 $value=$value+$diffArray[$j];
 $newArray[$j]=$value;
 $|=1;
 print $value, "\n";
 $j=$j+1;
 if($length-1==$j){
  $j=0;
 }
}
