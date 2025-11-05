#  ==============================================================================
# Author    : Jake Ginesin
# Authored  : 14 June 2024
# Purpose   : synthesize attacker gadgets for attackers that can drop, 
#             replay, and reorder messages on a channel
# ==============================================================================
import sys, re, subprocess, os, shutil
from typing import List

from utility import *
from model_generate import *

def show_help() -> None:
    msg=(
    "Usage: \n"
    "    python main.py [arguments] \n\n"
    "Arguments: \n"
    "    --model=path/to/model.pml                   Promela model to generate attackers on\n"
    "    --attacker=[replay,drop,reorder] \n"
    "    --chan=[chan1, chan2:int, ...]   Channels to synthesize attackers on. When specifying over ranges of\n"
    "                                                channels, you can give ranges or a list of values\n"
    "       --nocheck                                Don't check channel validity\n"
    # "       --nchan=[nat, nat, ...]             If the channel is a set of channels, how many attackers to synthesize?\n"
    "    --mem=[num]                                 Size of memory. Defaults to '3' \n"
    "       --mem=unbounded                          Use the unbounded memory gadget version (not recommended)\n"
    "    --output=path/to/file.pml                   Output file name\n"
    "    --eval                                      Evaluate the outputted file with Spin\n"
    "    --cleanup                                   Clean up the extra files spin creates, including Korg's \n"
    )
    print(msg)

    # assert "syntax error" not in stdout, "there seems to be a syntax error in the model"
    # assert "processes created" in stdout, "the spin model creates no processes ... check to see if it compiles"

def main() -> None:
    args = sys.argv[1:]  
    if len(args) == 0 or args[0] in ["help", "--help", "-h", "-help"]:
        show_help()
        sys.exit()

    mem = 3 # default

    for arg in args:
        if arg.startswith("--model="):
            model_path = arg.split("=", 1)[1]
        elif arg.startswith("--attacker="):
            attacker = arg.split("=", 1)[1]
        elif arg.startswith("--mem="):
            mem_read = arg.split("=", 1)[1]
        elif arg.startswith("--chan="):
            chans = arg.split("=", 1)[1]
        elif arg.startswith("--output="):
            out_file = arg.split("=", 1)[1]

    if "--eval" in args and not "--output" in args:
        out_file = "korg-promela-out.pml"

    if not model_path or not attacker or not mem or not chans or not out_file:
        print("error: all arguments are required. \n")
        show_help()
        sys.exit(1)

    unbounded = mem_read == "unbounded"
    if not unbounded : mem = int(mem_read)

    ensure_compile(model_path)
    model = fileRead(model_path)

    channels = parse_channels(fileReadLines(model_path))
    mchannels, mchannel_len = parse_mchannels(fileReadLines(model_path))
    model_with_attacker = str;
    assert mem >= 0, "memory value must be positive"

    chans_togen = set()

    # first, process the input
    mc = chans.split(",")
    for chan in mc:
        if ":" in chan:
            name, num_extr = chan[:chan.index(":")], chan[chan.index(":")+1:]
            if "-" in num_extr:
                a, b = list(map(lambda a: int(a), num_extr.split("-")))
                assert a < b
                assert a >= 0
                assert b < mchannel_len[name]
                for i in range(a,b+1):
                    chan_name = str(name) + "[" + str(i) + "]"
                    chans_togen.add(chan_name)
                    channels[chan_name] = mchannels[name]
            else:
                a = int(num_extr)
                assert a >= 0
                assert a < mchannel_len[name]
                chan_name = str(name) + "[" + str(a) + "]"
                chans_togen.add(chan_name)
                channels[chan_name] = mchannels[name]

        else : chans_togen.add(chan)

    print(chans_togen)

    for i in range(len(chans_togen)):
        chan = list(chans_togen)[i]

        if not "--nocheck" : assert chan in channels, "can't find "+str(chan)+" in model"

        match attacker:
            case "replay":
                if unbounded : attacker_gadget = gen_replay_unbounded(chan, channels[chan], i)
                else : attacker_gadget = gen_replay(chan, channels[chan], mem, i)
            case "drop":
                if unbounded : attacker_gadget = gen_drop_unbounded(chan, channels[chan], i)
                else : attacker_gadget = gen_drop(chan, channels[chan], mem, i)
            case "reorder":
                if unbounded : attacker_gadget = gen_reorder_unbounded(chan, channels[chan], i)
                else : attacker_gadget = gen_reorder(chan, channels[chan], mem, i)
            case _:
                print("error: inputted an invalid attacker model. \n")
                sys.exit(1)

        if model.rindex("};") >= model.rindex("}"):
            model = model[:model.rindex("};")+2] + "\n\n" + attacker_gadget + "\n" + model[model.rindex("};")+2:]
        else:
            model = model[:model.rindex("}")+1] + "\n\n" + attacker_gadget + "\n" + model[model.rindex("}")+1:]

    # Write the modified model to the output file
    with open(out_file, 'w') as file:
        file.write(model)

    if "--eval" in args:
        print()
        print("generated Promela file with attacker model gadget... now running SPIN on "+str(out_file) + "!\n")
        eval_model(out_file)

        if "--cleanup" in args:
            print("\nCleaning up Spin files...")
            cleanup_spin_files()
            try:
                os.remove(out_file)
                print(f"Removed: {out_file}")
            except OSError:
                pass


if __name__== "__main__":
    main()
