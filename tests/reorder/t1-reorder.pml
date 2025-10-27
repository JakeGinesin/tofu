// intended behavior: no violation
// explanation: the rearrange attacker gadget shouldn't be able to violate the claim, as 
// it doesn't have enough mem
chan c = [8] of { byte };
byte q=0;

init {
c!3;
c!5;
}

active proctype consume() {
MAIN:
  do 
  :: c ? 5 -> 
    q = q+1; 
    goto B1;
  od
B1:
  do 
  :: c ? 3 ->
    q = q + 1;
    goto END;
  od
END:
}

ltl proc {
  always !(q==2);
}
