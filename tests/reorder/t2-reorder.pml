// intended behavior: violation
// explanation: rearrange attacker has enough mem to do the rearrange attack
chan c = [8] of { byte };
byte q=0;

init {
c!3;
c!5;
c!7;
}

active proctype consume() {
MAIN:
  do 
  :: c ? 7 -> 
    q = q+1; 
    goto B1;
  od
B1:
  do 
  :: c ? 5 ->
    q = q + 1;
    goto B2;
  od
B2:
  do 
  :: c ? 3 ->
    q = q + 1;
    goto END;
  od
END:
}

ltl proc {
  always !(q==3);
}
