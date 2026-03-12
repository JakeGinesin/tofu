import sys, re, subprocess, os, shutil
from typing import List

def fileReadLines(fileName : str) -> str:
	try:
		txt = None
		with open(fileName, 'r') as fr:
			txt = fr.readlines()
		return txt
	except Exception:
		return ""

def fileRead(fileName : str) -> str:
	try:
		txt = None
		with open(fileName, 'r') as fr:
			txt = fr.read()
		return txt
	except Exception:
		return ""

def parse_channels(model : str) -> dict():
    channels = {}
    define_mapping = {}
    for line in model:
        if line.startswith("#define"):
            data = re.search(r"\#define\s*([A-Za-z\_\-]+)\s*([0-9])", line)
            if data is None : continue
            if not data.group(1) or not data.group(2) : continue
            define_mapping[data.group(1)] = int(data.group(2))
        if line.startswith("chan"):
            # parsing regular channels
            data = re.search(r"chan\s*([a-zA-Z\_\-]+).*\{(.+)\}", line)
            # note, we don't have to think very hard about parsing Promela types.
            # this is because mtype:whatever, mtype, and generic types are interchangable in Promela grammar
            if data is None : continue
            if not data.group(1) or not data.group(2) : continue
            name, ctype = data.group(1), data.group(2).replace(" ","").split(",")
            channels[name] = list(tuple(ctype))

            # data_multichan = re.search(r"chan\s*([A-Za-z\_\-0-9]+)\[([A-Za-z0-9\_\-]+)\].*\{(.+)\}", line)
            # m_name, m_cvalue, m_ctype = data.group(1), data.group(2), data.group(3).replace(" ","").split(",")

            #  try:
                #  m_cvalue = int(c_value)
            #  except ValueError:
                #  if type(m_cvalue) == str:
                    #  assert m_cvalue in define_mapping, "{c_value} isn't defined, yet your Promela file still parsed. Did you recursively define {c_value}?"
                    #  m_cvalue = define_mapping[m_cvalue]

            #  channels[m_name] = (m_cvalue, m_ctype)

        else : continue

    return channels

def parse_mchannels(model : str) -> (dict(), dict()):
    channels = {}
    channel_lens = {}
    define_mapping = {}
    for line in model:
        if line.startswith("#define"):
            data = re.search(r"\#define\s*([A-Za-z\_\-]+)\s*([0-9])", line)
            if data is None : continue
            if not data.group(1) or not data.group(2) : continue
            define_mapping[data.group(1)] = int(data.group(2))
            # print(define_mapping)
        if line.startswith("chan"):
            # parsing multichannels
            data_multichan = re.search(r"chan\s*([A-Za-z\_\-0-9]+)\[([A-Za-z0-9\_\-]+)\].*\{(.+)\}", line)

            if data_multichan is None:
                continue

            if data_multichan:
                m_name, m_cvalue, m_ctype = data_multichan.group(1), data_multichan.group(2), data_multichan.group(3).replace(" ","").split(",")
            else : continue

            try:
                m_cvalue = int(m_cvalue)
            except ValueError:
                if type(m_cvalue) == str:
                    assert m_cvalue in define_mapping, "{m_cvalue} isn't defined, yet your Promela file still parsed. Did you recursively define {c_value}?"
                    m_cvalue = define_mapping[m_cvalue]

            channels[m_name] = m_ctype
            channel_lens[m_name] = m_cvalue


        else : continue

    return channels, channel_lens

def ensure_compile(model_path : str) -> None:
    cmd = ['spin', '-a', model_path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    filename = os.path.basename(model_path)
    userdir = os.getcwd()

    # Convert bytes to string
    stdout = stdout.decode()
    stderr = stderr.decode()
    assert "error" not in stdout, "there seems to be a syntax error in the model!"
    # assert "syntax error" not in stdout, "there seems to be a syntax error in the model"
    # assert "processes created" in stdout, "the spin model creates no processes ... check to see if it compiles"

def eval_model(model_path : str) -> None:
    cmd = ['spin', '-run', '-a', '-DNOREDUCE', model_path]
    # Set text=True to get string output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    out = ""
    while True:
        output = proc.stdout.readline()
        if output == '' and proc.poll() is not None:
            break
        if output:
            out+=output
            print(output, end='')

    if "pan: wrote" in out: # we know we wrote a trail
        print("attack trace found!!!! printing!\n")
        cd = os.getcwd()
        if "/" in model_path:
            od = cd + model_path[model_path.rindex("/"):] + ".trail"
            shutil.copy(od, model_path + ".trail")
            shutil.copy(cd + "/pan", model_path[:model_path.rindex("/"):] + "/pan")
        else:
            od = cd + model_path + ".trail"
            # shutil.copy(od, model_path + ".trail")
            # shutil.copy(cd + "/pan", model_path[:model_path.rindex("/"):] + "/pan")

        cmd = ['spin', '-t0', '-s', '-r', model_path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        filename = os.path.basename(model_path)
        userdir = os.getcwd()

        # Convert bytes to string
        stdout = stdout.decode()
        stderr = stderr.decode()

        print(stdout)
    else:
        print()
        print("Korg's exhaustive search is complete, no attacks found :)")

def cleanup_spin_files() -> None:
    """Remove files generated by Spin"""
    files_to_remove = [
        'pan', 'pan.*', '*.trail', '_spin_nvr.tmp',
        '*.tcl', 'pan.b', 'pan.c', 'pan.h', 'pan.m', 'pan.t'
    ]
    for pattern in files_to_remove:
        if '*' in pattern:
            import glob
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                    print(f"Removed: {f}")
                except OSError:
                    pass
        else:
            try:
                os.remove(pattern)
                print(f"Removed: {pattern}")
            except OSError:
                pass
