/* liveness: simultaneous close resolution */
ltl phi7 {
    always (
        (state[0] == FinW1State && state[1] == FinW1State)
        implies 
            (eventually (state[0] == ClosedState) && 
             eventually (state[1] == ClosedState))
    )
}
