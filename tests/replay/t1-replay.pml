// INTENDED BEHAVIOR: violation
chan c = [8] of { byte };
byte q=1;

init {
c!5;
}

active proctype consume() {
MAIN:
  do 
  :: c ? 5 -> goto PROC1;
  od
PROC1:
  do 
  :: c ? 5 -> goto PROC2;
  od
PROC2:
  q=0;
}

ltl proc {
  always !(q == 0);
}
