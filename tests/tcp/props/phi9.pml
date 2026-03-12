/* safety: handshake cannot be bypassed */
ltl phi9 {
    always (
        (state[0] == ListenState) 
        implies 
            !(next (state[0] == EstState))
    )
}
