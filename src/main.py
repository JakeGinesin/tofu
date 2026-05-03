# ==============================================================================
# Author    : [redacted]
# Purpose   : synthesize attacker gadgets for attackers that can drop, 
#             replay, and reorder messages on a channel
# ==============================================================================
import sys
import subprocess
import os
import shutil
import argparse
from typing import List, Set, Dict, Tuple

from utility import *
from model_generate import *

def _parse_channel_selection(
    chans_str: str, 
    mchannels: Dict[str, List[str]], 
    mchannel_len: Dict[str, int],
    channels: Dict[str, List[str]]
) -> Set[str]:
    """
    Parses the user's channel selection string (e.g., "ch1,ch2:1-3,ch3:5").
    
    Raises:
        ValueError: If the format is invalid or ranges are out of bounds.
    """
    chans_togen = set()
    
    # first, process the input
    mc = chans_str.split(",")
    for chan in mc:
        if ":" in chan:
            try:
                name, num_extr = chan.split(":", 1)
                if name not in mchannel_len:
                    raise ValueError(f"unknown multi-channel '{name}'")
                
                max_len = mchannel_len[name]
                
                if "-" in num_extr:
                    a_str, b_str = num_extr.split("-", 1)
                    a, b = int(a_str), int(b_str)
                    
                    if not (0 <= a < b < max_len):
                        raise ValueError(f"invalid range '{a}-{b}' for {name} (max is {max_len-1})")
                        
                    for i in range(a, b + 1):
                        chan_name = f"{name}[{i}]"
                        chans_togen.add(chan_name)
                        channels[chan_name] = mchannels[name]
                else:
                    a = int(num_extr)
                    if not (0 <= a < max_len):
                         raise ValueError(f"invalid index '{a}' for {name} (max is {max_len-1})")

                    chan_name = f"{name}[{a}]"
                    chans_togen.add(chan_name)
                    channels[chan_name] = mchannels[name]
            
            except (ValueError, TypeError) as e:
                raise ValueError(f"invalid channel format: '{chan}'. {e}")

        else: 
            chans_togen.add(chan)
            
    return chans_togen

def _inject_attacker_code(model_content: str, attacker_gadget: str) -> str:
    """
    Injects the generated attacker gadget code into the Promela model string.
    
    Note: This injection method is fragile as it relies on finding the
    last '};' or '}' in the file.
    """
    try:
        # Original logic: find the last '};' or '}'
        if model_content.rindex("};") >= model_content.rindex("}"):
            idx = model_content.rindex("};") + 2
            return model_content[:idx] + "\n\n" + attacker_gadget + "\n" + model_content[idx:]
        else:
            idx = model_content.rindex("}") + 1
            return model_content[:idx] + "\n\n" + attacker_gadget + "\n" + model_content[idx:]
    except ValueError:
        # Fallback: append to the end if no '}' or '};' is found
        return model_content + "\n\n" + attacker_gadget


def parse_args() -> argparse.Namespace:
    """Configures and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Synthesize attacker gadgets for Promela models."
    )
    
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Promela model to generate attackers on"
    )
    parser.add_argument(
        "--attacker",
        type=str,
        required=True,
        choices=["replay", "drop", "reorder"],
        help="The type of attacker to synthesize"
    )
    parser.add_argument(
        "--chan",
        type=str,
        required=True,
        help="Channels to synthesize attackers on. (e.g., 'ch1,ch2:0-2,ch3:4')"
    )
    parser.add_argument(
        "--mem",
        type=str,
        default="3",
        help="Size of memory. Use 'unbounded' for unbounded memory. (default: 3)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file name. (default: korg-promela-out.pml if --eval is used)"
    )
    parser.add_argument(
        "--nocheck",
        action="store_true",
        help="Don't check channel validity"
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Evaluate the outputted file with Spin"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up the extra files spin creates, including Korg's"
    )
    
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # --- 1. Argument Validation ---
    
    # Handle output file logic
    out_file = args.output
    if args.eval and not args.output:
        out_file = "korg-promela-out.pml"
    elif not args.output:
        print("error: --output=path/to/file.pml is required when --eval is not used.", file=sys.stderr)
        sys.exit(1)

    # Handle memory logic
    unbounded = (args.mem == "unbounded")
    mem = 0
    if not unbounded:
        try:
            mem = int(args.mem)
            if mem < 0:
                raise ValueError("memory value must be positive")
        except ValueError as e:
            print(f"error: invalid --mem value. {e}", file=sys.stderr)
            sys.exit(1)

    # --- 2. Model Reading and Compilation Check ---
    
    # Check for file existence and read
    model_lines = fileReadLines(args.model)
    model_content = fileRead(args.model)
    if not model_content: # fileRead returns "" on error
        print(f"error: could not read model file at '{args.model}'", file=sys.stderr)
        sys.exit(1)

    # Ensure model compiles before proceeding
    try:
        ensure_compile(args.model)
    except AssertionError as e:
        print(f"error: Model compilation failed. {e}", file=sys.stderr)
        sys.exit(1)

    # --- 3. Model Parsing ---
    channels = parse_channels(model_lines)
    mchannels, mchannel_len = parse_mchannels(model_lines)

    try:
        chans_togen = _parse_channel_selection(
            args.chan, mchannels, mchannel_len, channels
        )
    except ValueError as e:
        print(f"error: Failed to parse --chan argument. {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating attackers for: {chans_togen}")

    # --- 4. Attacker Generation ---
    for i, chan in enumerate(list(chans_togen)):
        if not args.nocheck and chan not in channels:
            print(f"error: can't find channel '{chan}' in model. (Use --nocheck to override)", file=sys.stderr)
            sys.exit(1)

        attacker_gadget = ""
        chan_type = channels.get(chan, []) # Default to empty list if not found (and --nocheck)
        
        match args.attacker:
            case "replay":
                attacker_gadget = gen_replay_unbounded(chan, chan_type, i) if unbounded \
                           else gen_replay(chan, chan_type, mem, i)
            case "drop":
                attacker_gadget = gen_drop_unbounded(chan, chan_type, i) if unbounded \
                           else gen_drop(chan, chan_type, mem, i)
            case "reorder":
                attacker_gadget = gen_reorder_unbounded(chan, chan_type, i) if unbounded \
                           else gen_reorder(chan, chan_type, mem, i)
            case _:
                # This should be unreachable due to argparse `choices`
                print(f"error: invalid attacker model '{args.attacker}'.", file=sys.stderr)
                sys.exit(1)
        
        # Inject the generated gadget into the model
        model_content = _inject_attacker_code(model_content, attacker_gadget)

    # --- 5. Write Output ---
    try:
        with open(out_file, 'w') as file:
            file.write(model_content)
    except IOError as e:
        print(f"error: could not write to output file {out_file}. {e}", file=sys.stderr)
        sys.exit(1)

    # --- 6. Evaluate and Cleanup ---
    if args.eval:
        print(f"\nGenerated Promela file... now running SPIN on {out_file}!\n")
        eval_model(out_file)

        if args.cleanup:
            print("\nCleaning up Spin files...")
            cleanup_spin_files()
            try:
                os.remove(out_file)
                print(f"Removed: {out_file}")
            except OSError:
                pass


if __name__ == "__main__":
    main()
