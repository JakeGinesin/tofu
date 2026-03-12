mtype = { SYN, FIN, ACK }

chan AtoB = [2] of { mtype };
chan BtoA = [2] of { mtype };

int state[2];

#define ClosedState    0
#define ListenState    1
#define SynSentState   2
#define SynRecState    3
#define EstState       4
#define FinW1State     5
#define CloseWaitState 6
#define FinW2State     7
#define ClosingState   8
#define LastAckState   9
#define TimeWaitState  10

proctype TCP(chan snd, rcv; int i) {
    mtype msg;
CLOSED:
    state[i] = ClosedState;
    if
    :: goto LISTEN;
    :: snd ! SYN; goto SYN_SENT;
    fi;

LISTEN:
    state[i] = ListenState;
    do
    :: rcv ? msg -> 
        if 
        :: msg == SYN -> snd ! SYN; snd ! ACK; goto SYN_RECEIVED;
        :: else -> skip;
        fi
    :: timeout -> goto CLOSED;
    od;

SYN_SENT:
    state[i] = SynSentState;
    do
    :: rcv ? msg ->
        if
        :: msg == SYN -> snd ! ACK; goto SYN_RECEIVED;
        :: msg == ACK -> 
            do
            :: rcv ? msg -> 
                if 
                :: msg == SYN -> snd ! ACK; goto ESTABLISHED;
                :: else -> skip;
                fi
            :: timeout -> goto CLOSED;
            od
        :: else -> skip;
        fi
    :: timeout -> goto CLOSED;
    od;

SYN_RECEIVED:
    state[i] = SynRecState;
    do
    :: rcv ? msg ->
        if
        :: msg == ACK -> goto ESTABLISHED;
        :: else -> skip;
        fi
    :: timeout -> goto CLOSED;
    od;

ESTABLISHED:
    state[i] = EstState;
    do
    :: snd ! FIN; goto FIN_WAIT_1;
    :: rcv ? msg ->
        if
        :: msg == FIN -> snd ! ACK; goto CLOSE_WAIT;
        :: else -> skip;
        fi
    od;

FIN_WAIT_1:
    state[i] = FinW1State;
    do
    :: rcv ? msg ->
        if
        :: msg == FIN -> snd ! ACK; goto CLOSING;
        :: msg == ACK -> goto FIN_WAIT_2;
        :: else -> skip;
        fi
    od;

FIN_WAIT_2:
    state[i] = FinW2State;
    do
    :: rcv ? msg ->
        if
        :: msg == FIN -> snd ! ACK; goto TIME_WAIT;
        :: else -> skip;
        fi
    od;

CLOSING:
    state[i] = ClosingState;
    do
    :: rcv ? msg ->
        if
        :: msg == ACK -> goto TIME_WAIT;
        :: else -> skip;
        fi
    od;

CLOSE_WAIT:
    state[i] = CloseWaitState;
    snd ! FIN; goto LAST_ACK;

LAST_ACK:
    state[i] = LastAckState;
    do
    :: rcv ? msg ->
        if
        :: msg == ACK -> goto CLOSED;
        :: else -> skip;
        fi
    od;

TIME_WAIT:
    state[i] = TimeWaitState;
    goto CLOSED;
}

init {
    state[0] = ClosedState;
    state[1] = ClosedState;
    atomic {
        run TCP(AtoB, BtoA, 0);
        run TCP(BtoA, AtoB, 1);
    }
}

/* safety: strict closing transitions */
ltl phi6 {
	always (
		(state[0] == ClosingState)
			implies
				(next (state[0] == ClosingState ||
					   state[0] == ClosedState))
	)
}
