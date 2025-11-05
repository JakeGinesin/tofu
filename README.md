# Korg, reborn

# TODO:
- [x] nix flake here
- [x] fix weird spin errors(?)
    - jake note: pinned specific working SPIN version using Nix
- [x] add attackers that only do specifically n queries
    - limitation: you cannot choose only *n* queries for the dropping attacker; trace violations can happen at any time
- [x] add attackers to do <= n queries
- [x] add attackers that can do attacks with an unbounded number of messages
- [x] add a test suite
- [x] make the impl more robust; do more SWE
- [x] add no self-deadlock experiments
    - I envision this would be: providing an eventually-style LTL query, sending messages onto an open channel, and asserting that the gadget doesn't somehow deadlock with itself
- [ ] add raft, TCP, SCTP, ABP experiments from old Korg impl to the test suite
- [ ] add labels on trace logging to gadgets
- [ ] modify the paper? spin workshop?

# Notes
- Sound and complete attack discovery for replay, dropping, and reordering attacks on channels
    - possible because of the finite-state modeling spin does
- Limiting the number of messages a drop/replay/reorder attacker can reason about has the ability to significantly reduce the searchspace, especially when dealing with larger models. Although KORG is always decidable, sound, and complete, using the unbounded attacker is inadvisable in practice because spin must reason about *all* such permutations of possible drop, replay, and reorder sequences, thereby increasing the search space factorially.
- One explicit limitation of the replay attacker is not being able to transition back to listening for packets after replaying
- Maybe change the title to: Korg: Automated analysis of channel faults
