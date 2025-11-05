chan c = [8] of { byte };
byte q=1;

init {
c!5;
c!5;
c!5;
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
