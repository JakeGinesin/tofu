/* liveness: active close eventually terminates */
ltl phi8 {
    always (
        (state[0] == FinW1State) implies (eventually (state[0] == ClosedState))
    )
}
