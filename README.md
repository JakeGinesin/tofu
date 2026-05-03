# Automated Channel Fault Analysis with Tofu

## Installation and Tests
- Install nix
- Run `nix develop`
- Execute the test harnesses with `test_harness.py`:

```
$ test_harness tests/tcp.yaml # TCP tests
$ test_harness tests/abp.yaml # ABP tests
$ test_harness tests/tests.yaml # general correctness tests
```
Each test comes with a description - check out the respective YAML files

A full tutorial is available in [TUTORIAL.MD](TUTORIAL.md)

## Why Tofu?
Named after the following cat, which was in-turn named after the food:

![Tofu](tofu.png)
