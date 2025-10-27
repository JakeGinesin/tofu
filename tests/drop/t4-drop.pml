// INTENDED BEHAVIOR: violation
// explanation: drop attacker should be able to find the attack in the middle of the chan
chan c = [8] of { byte };
byte q=1;

init {
c!3;
c!5;
c!6;

}

active proctype consume() {
MAIN:
  do 
  :: c ? 5 -> goto PROC;
  od
PROC:
  q=0;
}

ltl proc {
  eventually (q == 0);
}
