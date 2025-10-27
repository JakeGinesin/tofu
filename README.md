# Korg, reborn

# TODO:
- [x] fix weird spin errors(?)
- [ ] add attackers that only do specifically n queries
    - limitation: you cannot choose only *n* queries for the dropping attacker
- [ ] add attackers to do <= n queries
- [x] add a test suite
- [ ] modify the paper? spin workshop?
- [x] nix flake here lol

# Notes
- Sound and complete attack discovery for replay, dropping, and reordering attacks on channels
    - possible because of the finite-state modeling spin does
- Limiting the number of messages a drop/replay/reorder attacker can reason about has the ability to significantly reduce the searchspace, especially when dealing with larger models. Although KORG is always decidable, sound, and complete, using the unbounded attacker is inadvisable in practice because spin must reason about *all* such permutations of possible drop, replay, and reorder sequences, thereby increasing the search space factorially.
