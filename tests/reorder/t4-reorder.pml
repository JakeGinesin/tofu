// intended behavior: violation
// explanation: rearrange attacker does not have enough mem
chan c = [1] of { byte };
byte q=0;

init {
c!3;
c!5;
c!7;
}

active proctype consume() {
MAIN:
  do 
  :: c ? 3 -> 
    goto B1;
  od
B1:
  do 
  :: c ? 7 ->
    goto B2;
  od
B2:
  do 
  :: c ? 5 ->
    goto END;
  od
END:
q = 1;
}

ltl proc {
  always !(q == 1);
}
