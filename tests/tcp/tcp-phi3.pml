// models: phi1, phi2, phi3, phi5
// does not model: phi4, phi7
// not yet implemented: phi6
mtype = { SYN, FIN, ACK, ABORT, CLOSE, RST, OPEN }

chan AtoN = [2] of { mtype };
chan NtoA = [2] of { mtype };
chan BtoN = [2] of { mtype };
chan NtoB = [2] of { mtype };

int state[2];
int pids[2];

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
#define EndState       -1

#define leftConnecting (state[0] == ListenState && state[1] == SynSentState)
#define leftEstablished (state[0] == EstState)
#define rightEstablished (state[1] == EstState)
#define leftClosed (state[0] == ClosedState)

proctype TCP(chan snd, rcv; int i) {
	pids[i] = _pid;
CLOSED:
	state[i] = ClosedState;
  do
	/* Passive open */
	:: goto LISTEN;
	/* Active open */
	:: snd ! SYN; goto SYN_SENT;
	/* Terminate */
	:: goto end;
  od
LISTEN:
	state[i] = ListenState;
  do
	:: rcv ? SYN -> 
    atomic {
      snd ! SYN; 
      snd ! ACK; 
      goto SYN_RECEIVED;
    }
	/* Simultaneous LISTEN */
  :: rcv ? _ -> skip;
	:: timeout -> goto CLOSED; 
  od
SYN_SENT:
	state[i] = SynSentState;
  do
	:: rcv ? SYN;
		if
		/* Standard behavior */
		:: rcv ? ACK -> snd ! ACK; goto ESTABLISHED;
		/* Simultaneous open */
		:: snd ! ACK; goto SYN_RECEIVED;
		fi
	:: rcv ? ACK; 
    do
    :: rcv ? SYN -> 
      snd ! ACK; 
      goto ESTABLISHED;
    :: rcv ? _ -> skip;
    od
  :: rcv ? _ -> skip;
	:: timeout -> goto CLOSED; /* Timeout */
  od
SYN_RECEIVED:
	state[i] = SynRecState;
  do
  :: rcv ? ACK -> goto ESTABLISHED;
  :: rcv ? _ -> skip;
  od
	/* We may want to consider putting a timeout -> CLOSED here. */
ESTABLISHED:
	state[i] = EstState;
  do 
	/* Close - initiator sequence */
	:: snd ! FIN; goto FIN_WAIT_1;
	/* Close - responder sequence */
	:: rcv ? FIN -> 
    snd ! ACK; 
    goto CLOSE_WAIT;
  :: rcv ? _ -> skip;
  od
FIN_WAIT_1:
	state[i] = FinW1State;
  do
	/* Simultaneous close */
	:: rcv ? FIN -> 
    snd ! ACK; 
    goto CLOSING;
	/* Standard close */
	:: rcv ? ACK -> goto FIN_WAIT_2;
  :: rcv ? _ -> skip;
  od
CLOSE_WAIT:
	state[i] = CloseWaitState;
  do
	:: snd ! FIN; goto LAST_ACK;
  :: rcv ? _ -> skip;
  od
FIN_WAIT_2:
	state[i] = FinW2State;
  do
  :: rcv ? FIN -> 
    snd ! ACK; 
    goto TIME_WAIT;
  :: rcv ? _ -> skip;
  od
CLOSING:
	state[i] = ClosingState;
  do 
	:: rcv ? ACK -> goto TIME_WAIT;
  :: rcv ? _ -> skip;
  od
LAST_ACK:
	state[i] = LastAckState;
  do
	:: rcv ? ACK -> goto CLOSED;
  :: rcv ? _ -> skip;
  od 
TIME_WAIT:
	state[i] = TimeWaitState;
	goto CLOSED;
end:
	state[i] = EndState;
}

init {
	state[0] = ClosedState;
	state[1] = ClosedState;
	run TCP(AtoN, NtoA, 0);
	run TCP(BtoN, NtoB, 1);
}

/* liveness: no infinite stalls/deadlocks */
ltl phi3 {
  !(eventually (((always (state[0] == SynSentState))   ||
                 (always (state[0] == SynRecState))    ||
                 (always (state[0] == EstState))       ||
                 (always (state[0] == FinW1State))     ||
                 (always (state[0] == CloseWaitState)) ||
                 (always (state[0] == FinW2State))     ||
                 (always (state[0] == ClosingState))   ||
                 (always (state[0] == LastAckState))   ||
                 (always (state[0] == TimeWaitState)))
                &&
                ((always (state[1] == SynSentState))   ||
                 (always (state[1] == SynRecState))    ||
                 (always (state[1] == EstState))       ||
                 (always (state[1] == FinW1State))     ||
                 (always (state[1] == CloseWaitState)) ||
                 (always (state[1] == FinW2State))     ||
                 (always (state[1] == ClosingState))   ||
                 (always (state[1] == LastAckState))   ||
                 (always (state[1] == TimeWaitState)))))
}
