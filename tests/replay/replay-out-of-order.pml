// INTENDED BEHAVIOR: violation
// explanation: replay, but in a different order than received
chan c = [8] of { byte };
byte q=1;

init {
c!5;
c!3;
}

active proctype consume() {
MAIN:
  do 
  :: c ? 5 -> goto PROC1;
  od
PROC1:
  do 
  :: c ? 3 -> goto PROC2;
  od
PROC2:
  do 
  :: c ? 3 -> goto PROC3;
  od
PROC3:
  do 
  :: c ? 5 -> goto PROC4;
  od
PROC4:
  q=0;
}

ltl proc {
  always !(q == 0);
}
