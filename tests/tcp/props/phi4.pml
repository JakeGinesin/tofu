/* liveness: simultanous open */ 
ltl phi4 {
	always (
		(state[0] == SynSentState && 
		 state[1] == SynSentState)
		
		implies
			
			((eventually state[0] == EstState) &&
		     (eventually state[1] == EstState)))
}
