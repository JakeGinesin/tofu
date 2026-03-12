/* safety: strict closing transitions */
ltl phi6 {
	always (
		(state[0] == ClosingState)
			implies
				(next (state[0] == ClosingState ||
					   state[0] == ClosedState))
	)
}
