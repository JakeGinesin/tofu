import yaml, sys
import sys, re, subprocess, os, shutil
from typing import List

passed = 0
failed = 0

def show_help() -> None:
    msg="""  Usage:
    python3 test_harness.py tests/tests.yaml
    """
    print(msg)

def run_spin_test(name, data):
    global passed
    global failed
    data = {k: v for d in data for k, v in d.items()}
    cmd = data['command']
    intended = data['intended']
    explanation = data['intended']

    proc = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    out = ""
    while True:
        output = proc.stdout.readline()
        if output == '' and proc.poll() is not None:
            break
        if output:
            out += output

    res = None
    if "assertion violated" in out:
        res = "property violation"
    elif "acceptance cycle" in out:
        res = "acceptance cycle"
    else : res = "no violation"

    if res == intended:
        print("passed: " + name)
        passed+=1
    else:
        print("FAILED: " + name + " - got '" + res + "', expected '" + intended + "'")
        failed+=1


def main() -> None:
    args = sys.argv[1:]  

    if len(args) == 0 or args[0] in ["help", "--help", "-h", "-help"]:
        show_help()
        sys.exit()

    test_file = args[0]

    file = open(test_file, 'r')
    data = yaml.safe_load(file)
    for i in data:
        run_spin_test(i, data[i])

    print("")
    print("SUMMARY:")
    print("passed: " + str(passed) + "; failed: " + str(failed))

main()
