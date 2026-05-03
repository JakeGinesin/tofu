# Tutorial

Tofu synthesizes attacker gadgets (drop / replay / reorder) on top of an existing Promela model, then hands the combined model to Spin. If the LTL property breaks, the attacker found an attack.

## Setup

```
$ nix develop
```

The flake pins `nixpkgs` and a specific `spin` revision (see `flake.lock`), so the toolchain is reproducible across machines.

## CLI

```
python src/main.py \
  --model=<path>.pml \
  --attacker={drop,replay,reorder} \
  --chan=<chan>[,<chan>...] \
  --mem=<int|unbounded> \
  --output=<path>.pml \
  [--eval] [--cleanup] [--nocheck]
```

- `--mem` bounds the attacker's memory (number of messages it can buffer / drop). Use `unbounded` to remove the bound.
- `--chan` accepts a comma-separated list. Multi-channel arrays use `name:i` or `name:a-b`.
- `--eval` runs Spin on the output. `--cleanup` removes Spin artifacts (`pan*`, `*.trail`, `_spin_nvr.tmp`) and the output `.pml` after evaluation.

## Writing a Model

A model has three parts: a channel, a consumer that walks a state machine on that channel, and an LTL property.

Save as `tests/example/tut.pml`:

```promela
// INTENDED BEHAVIOR: violation under replay, mem=1
chan c = [8] of { byte };
byte q = 1;

init {
  c!5;
}

active proctype consume() {
MAIN:
  do
  :: c ? 5 -> goto PROC1;
  od
PROC1:
  do
  :: c ? 5 -> goto PROC2;
  od
PROC2:
  q = 0;
}

ltl proc {
  always !(q == 0);
}
```

The honest channel only carries one `5`, so `consume` should stall at `PROC1`. A replay attacker with `mem=1` can re-emit the consumed `5`, advancing the consumer to `PROC2` and falsifying the property.

## Running the Tool

```
$ python src/main.py --model=tests/example/tut.pml \
    --attacker=replay --chan=c \
    --output=temp.pml --mem=1 --eval --cleanup
```

Outputs to look for in Spin's report:

| Spin output            | Meaning                                                          |
|------------------------|------------------------------------------------------------------|
| `assertion violated`   | LTL safety property violated (attack found)                      |
| `acceptance cycle`     | LTL liveness violated (attacker stalls progress)                 |
| neither                | No violation; attacker (at this `--mem`) cannot break the model  |

For the model above, expect a property violation. Drop `--mem` to `0` or switch to `--attacker=drop` and the violation disappears — the attacker no longer has the budget.

## Test Harness

Each `tests/*.yaml` entry pins a command and its intended outcome:

```yaml
my-test:
  - command: python src/main.py --model=tests/example/tut.pml --attacker=replay --chan=c --output=temp.pml --eval --cleanup --mem=1
  - intended: property violation
  - explanation: replay attacker can re-emit the consumed 5
```

Run the suite:

```
$ python test_harness.py tests/tests.yaml
$ python test_harness.py tests/tcp.yaml
$ python test_harness.py tests/abp.yaml
```

The harness diffs Spin's verdict against `intended` and prints a pass/fail summary.
