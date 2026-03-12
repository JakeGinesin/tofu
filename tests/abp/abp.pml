mtype = { DATA0, DATA1, ACK0, ACK1 }

chan AtoB = [1] of { mtype }
chan BtoA = [1] of { mtype }

mtype ackA, ackB;
byte seqA = 0;
byte seqB = 0;

mtype packetA, packetB;

active proctype A()
{
    do
    :: 
       if
       :: seqA == 0 -> packetA = DATA0
       :: else -> packetA = DATA1
       fi;
       AtoB!packetA;
       do
       :: BtoA?ackA ->
           if
           :: (seqA == 0 && ackA == ACK0) || (seqA == 1 && ackA == ACK1) ->
               seqA = 1 - seqA; 
               break
           :: else -> skip;
           fi
       :: 
           AtoB!packetA
       od
    od
}

active proctype B()
{
    do
    :: AtoB?packetB ->
        if
        :: (seqB == 0 && packetB == DATA0) || (seqB == 1 && packetB == DATA1) ->
            if
            :: seqB == 0 -> ackB = ACK0
            :: else -> ackB = ACK1
            fi;
            BtoA!ackB;
            seqB = 1 - seqB; 
        :: else ->
            if
            :: seqB == 0 -> ackB = ACK1
            :: else -> ackB = ACK0
            fi;
            BtoA!ackB;
        fi
    od
}

ltl liveness {
  always ((packetA != packetB) implies eventually (packetA == packetB))
}
