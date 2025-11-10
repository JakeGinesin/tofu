import sys, re, subprocess, os, shutil
from typing import List

#  def gen_replay_old(chan : str, chan_type : List[str], mem : int, index : int) -> str:
    #  ret_string = ""

    #  ret_string+= "chan attacker_mem_"+str(index)+" = ["+str(mem)+"] of " + ("{ " + str(chan_type)[1:-1] + " }") .replace("'","") + ";\n"
    #  ret_string+= "\n"

    #  ret_string+= "active proctype attacker_replay_"+str(index)+"() {\n"

    #  item_arr = []
    #  item_count = 0

    #  # formulate string of general message input variables
    #  for item in chan_type:
        #  item_arr.append("b_" + str(item_count))
        #  ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        #  item_count+=1

    #  fs = (str([item for item in item_arr])[1:-1]).replace("'","")

    #  ret_string+="int i = "+str(mem)+";\n"
    #  ret_string+="int b;\n"
    #  ret_string+="CONSUME:\n"
    #  ret_string+="  do\n"
    #  ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    #  ret_string+="   "+str(chan)+" ? <"+fs+"> -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    #  ret_string+="    i--;\n"
    #  ret_string+="    if\n"
    #  ret_string+="    :: i == 0 -> goto REPLAY;\n"
    #  ret_string+="    :: i != 0 -> goto CONSUME;\n"
    #  ret_string+="    fi\n"
    #  ret_string+="    }\n"
    #  ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    #  ret_string+="    b = len("+str(chan)+");\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: b != len("+str(chan)+") -> goto CONSUME;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  od\n"
    #  ret_string+="REPLAY:\n"
    #  ret_string+="  do\n"
    #  ret_string+="  :: atomic {\n"
    #  ret_string+="    int am;\n"
    #  ret_string+="    select(am : 0 .. len(attacker_mem_"+str(index)+")-1);\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: am != 0 ->\n"
    #  ret_string+="      am = am-1;\n"
    #  ret_string+="      attacker_mem_"+str(index)+" ? "+fs+" -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    #  ret_string+="    :: am == 0 ->\n"
    #  ret_string+="      attacker_mem_"+str(index)+" ? "+fs+" -> "+str(chan)+" ! "+fs+";\n"
    #  ret_string+="      break;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    #  ret_string+="    b = len("+str(chan)+");\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: b != len("+str(chan)+") -> goto REPLAY;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  :: atomic {attacker_mem_"+str(index)+" ? "+fs+"; }\n"
    #  ret_string+="  :: empty(attacker_mem_"+str(index)+") -> goto BREAK;\n"
    #  ret_string+="  od\n"
    #  ret_string+="BREAK:\n"
    #  ret_string+="}\n"

    #  return ret_string

def gen_replay(chan : str, chan_type : List[str], mem : int, index : int) -> str:
    ret_string = ""

    ret_string+= "chan attacker_mem_"+str(index)+" = ["+str(mem)+"] of " + ("{ " + str(chan_type)[1:-1] + " }") .replace("'","") + ";\n"
    ret_string+= "\n"

    ret_string+= "active proctype attacker_replay_"+str(index)+"() {\n"

    item_arr = []
    item_count = 0

    # formulate string of general message input variables
    for item in chan_type:
        item_arr.append("b_" + str(item_count))
        ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        item_count+=1

    fs = (str([item for item in item_arr])[1:-1]).replace("'","")

    ret_string+="int i = "+str(mem)+";\n"
    ret_string+="int b;\n"
    ret_string+="CONSUME:\n"
    ret_string+="  do\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    ret_string+="   "+str(chan)+" ? <"+fs+"> -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    ret_string+="    i--;\n"
    ret_string+="    if\n"
    ret_string+="    :: i == 0 -> goto REPLAY;\n"
    ret_string+="    :: i != 0 -> {\n"
    ret_string+="      do\n"
    ret_string+="      :: goto CONSUME\n"
    ret_string+="      :: goto REPLAY\n"
    ret_string+="      od\n"
    ret_string+="      }\n"
    ret_string+="    fi\n"
    ret_string+="    }\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto CONSUME;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  od\n"
    ret_string+="REPLAY:\n"
    ret_string+="  do\n"
    ret_string+="  :: atomic {\n"
    ret_string+="    int am;\n"
    ret_string+="    select(am : 0 .. len(attacker_mem_"+str(index)+")-1);\n"
    ret_string+="    do\n"
    ret_string+="    :: am != 0 ->\n"
    ret_string+="      am = am-1;\n"
    ret_string+="      attacker_mem_"+str(index)+" ? "+fs+" -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    ret_string+="    :: am == 0 ->\n"
    ret_string+="      do\n"
    ret_string+="      :: attacker_mem_"+str(index)+" ? ["+fs+"] -> "+str(chan)+" ! "+fs+"; break;\n"
    ret_string+="      :: attacker_mem_"+str(index)+" ? "+fs+" -> "+str(chan)+" ! "+fs+"; break;\n"
    ret_string+="      od\n"
    ret_string+="      break;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto REPLAY;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: i != 0 -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto CONSUME;\n"
    ret_string+="    od\n"
    ret_string+="  }\n"
    ret_string+="  :: atomic {attacker_mem_"+str(index)+" ? "+fs+"; }\n"
    ret_string+="  :: empty(attacker_mem_"+str(index)+") -> goto BREAK;\n"
    ret_string+="  od\n"
    ret_string+="BREAK:\n"
    ret_string+="}\n"

    return ret_string

def gen_replay_unbounded(chan : str, chan_type : List[str], mem : int, index : int) -> str:
    ret_string = ""

    ret_string+= "chan attacker_mem_"+str(index)+" = [99] of " + ("{ " + str(chan_type)[1:-1] + " }") .replace("'","") + ";\n"
    ret_string+= "\n"

    ret_string+= "active proctype attacker_replay_"+str(index)+"() {\n"

    item_arr = []
    item_count = 0

    # formulate string of general message input variables
    for item in chan_type:
        item_arr.append("b_" + str(item_count))
        ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        item_count+=1

    fs = (str([item for item in item_arr])[1:-1]).replace("'","")

    ret_string+="int b;\n"
    ret_string+="CONSUME:\n"
    ret_string+="  do\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    ret_string+="   "+str(chan)+" ? <"+fs+"> -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    ret_string+="    do\n"
    ret_string+="    :: goto CONSUME\n"
    ret_string+="    :: goto REPLAY\n"
    ret_string+="    od\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto CONSUME;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  od\n"
    ret_string+="REPLAY:\n"
    ret_string+="  do\n"
    ret_string+="  :: atomic {\n"
    ret_string+="    int am;\n"
    ret_string+="    select(am : 0 .. len(attacker_mem_"+str(index)+")-1);\n"
    ret_string+="    do\n"
    ret_string+="    :: am != 0 ->\n"
    ret_string+="      am = am-1;\n"
    ret_string+="      attacker_mem_"+str(index)+" ? "+fs+" -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    ret_string+="    :: am == 0 ->\n"
    ret_string+="      do\n"
    ret_string+="      :: attacker_mem_"+str(index)+" ? ["+fs+"] -> "+str(chan)+" ! "+fs+"; break;\n"
    ret_string+="      :: attacker_mem_"+str(index)+" ? "+fs+" -> "+str(chan)+" ! "+fs+"; break;\n"
    ret_string+="      od\n"
    ret_string+="      break;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto REPLAY;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto CONSUME;\n"
    ret_string+="    od\n"
    ret_string+="  }\n"
    ret_string+="  :: atomic {attacker_mem_"+str(index)+" ? "+fs+"; }\n"
    ret_string+="  :: empty(attacker_mem_"+str(index)+") -> goto BREAK;\n"
    ret_string+="  od\n"
    ret_string+="BREAK:\n"
    ret_string+="}\n"

    return ret_string

#  def gen_replay_unbounded_old(chan : str, chan_type : List[str], index : int) -> str:
    #  ret_string = ""

    #  ret_string+= "chan attacker_mem_"+str(index)+" = [99] of " + ("{ " + str(chan_type)[1:-1] + " }") .replace("'","") + ";\n"
    #  ret_string+= "\n"

    #  ret_string+= "active proctype attacker_replay_"+str(index)+"() {\n"

    #  item_arr = []
    #  item_count = 0

    #  # formulate string of general message input variables
    #  for item in chan_type:
        #  item_arr.append("b_" + str(item_count))
        #  ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        #  item_count+=1

    #  fs = (str([item for item in item_arr])[1:-1]).replace("'","")

    #  ret_string+="int b;\n"
    #  ret_string+="CONSUME:\n"
    #  ret_string+="  do\n"
    #  ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    #  ret_string+="   "+str(chan)+" ? <"+fs+"> -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: goto REPLAY;\n"
    #  ret_string+="    :: goto CONSUME;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    #  ret_string+="    b = len("+str(chan)+");\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: b != len("+str(chan)+") -> goto CONSUME;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  od\n"
    #  ret_string+="REPLAY:\n"
    #  ret_string+="  do\n"
    #  ret_string+="  :: atomic {\n"
    #  ret_string+="    int am;\n"
    #  ret_string+="    select(am : 0 .. len(attacker_mem_"+str(index)+")-1);\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: am != 0 ->\n"
    #  ret_string+="      am = am-1;\n"
    #  ret_string+="      attacker_mem_"+str(index)+" ? "+fs+" -> attacker_mem_"+str(index)+" ! "+fs+";\n"
    #  ret_string+="    :: am == 0 ->\n"
    #  ret_string+="      attacker_mem_"+str(index)+" ? "+fs+" -> "+str(chan)+" ! "+fs+";\n"
    #  ret_string+="      break;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> atomic {\n"
    #  ret_string+="    b = len("+str(chan)+");\n"
    #  ret_string+="    do\n"
    #  ret_string+="    :: b != len("+str(chan)+") -> goto REPLAY;\n"
    #  ret_string+="    od\n"
    #  ret_string+="    }\n"
    #  ret_string+="  :: atomic {attacker_mem_"+str(index)+" ? "+fs+"; }\n"
    #  ret_string+="  :: empty(attacker_mem_"+str(index)+") -> goto BREAK;\n"
    #  ret_string+="  od\n"
    #  ret_string+="BREAK:\n"
    #  ret_string+="}\n"

    #  return ret_string


def gen_reorder(chan : str, chan_type : List[str], mem : int, index : int) -> str:
    ret_string = ""

    ret_string+= "chan attacker_mem_"+str(index)+" = ["+str(mem)+"] of " + ("{ " + str(chan_type)[1:-1] + " }") .replace("'","") + ";\n"
    ret_string+= "\n"

    ret_string+= "active proctype attacker_reorder_"+str(index)+"() priority 99 {\n"

    item_arr = []
    item_count = 0

    attacker_mem = "attacker_mem_" + str(index)

    # formulate string of general message input variables
    for item in chan_type:
        item_arr.append("b_" + str(item_count))
        ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        item_count+=1

    fs = (str([item for item in item_arr])[1:-1]).replace("'","")
    ret_string+="int i = "+str(mem)+";\n"
    ret_string+="int b;\n"
    ret_string+="INIT:\n"
    ret_string+="do\n"
    #  ret_string+="  :: true -> {\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="      b = len("+str(chan)+");\n"
    ret_string+="      do\n"
    ret_string+="      :: b != len("+str(chan)+") -> goto INIT;\n"
    ret_string+="      od\n"
    ret_string+="    }\n"
    ret_string+="  :: goto CONSUME;\n"
    ret_string+="od\n"
    ret_string+="CONSUME:\n"
    ret_string+="do\n"
    ret_string+="  :: "+str(chan)+" ? "+str(fs)+" -> atomic {\n"
    ret_string+="    "+str(attacker_mem)+" ! "+str(fs)+";\n"
    ret_string+="    i--;\n"
    ret_string+="    if\n"
    ret_string+="    :: i == 0 -> goto REPLAY;\n"
    ret_string+="    :: i != 0 -> goto CONSUME;\n"
    ret_string+="    fi\n"
    ret_string+="  }\n"
    ret_string+="od\n"
    ret_string+="REPLAY:\n"
    ret_string+="  do\n"
    ret_string+="  :: atomic {\n"
    ret_string+="  int am;\n"
    ret_string+="    select(am : 0 .. len("+str(attacker_mem)+")-1);\n"
    ret_string+="    do\n"
    ret_string+="    :: am != 0 -> \n"
    ret_string+="      am = am-1;\n"
    ret_string+="      "+str(attacker_mem)+" ? "+str(fs)+" -> "+str(attacker_mem)+" ! "+str(fs)+";\n"
    ret_string+="    :: am == 0 ->\n"
    ret_string+="      "+str(attacker_mem)+" ? "+str(fs)+" -> "+str(chan)+" ! "+str(fs)+";\n"
    ret_string+="      break;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: empty("+str(attacker_mem)+") -> goto BREAK;\n"
    ret_string+="  od\n"
    ret_string+="BREAK:\n"
    ret_string+="}\n"

    return ret_string

def gen_reorder_unbounded(chan : str, chan_type : List[str], index : int) -> str:
    ret_string = ""

    ret_string+= "chan attacker_mem_"+str(index)+" = [99] of " + ("{ " + str(chan_type)[1:-1] + " }") .replace("'","") + ";\n"
    ret_string+= "\n"

    ret_string+= "active proctype attacker_reorder_"+str(index)+"() priority 99 {\n"

    item_arr = []
    item_count = 0

    attacker_mem = "attacker_mem_" + str(index)

    # formulate string of general message input variables
    for item in chan_type:
        item_arr.append("b_" + str(item_count))
        ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        item_count+=1

    fs = (str([item for item in item_arr])[1:-1]).replace("'","")
    ret_string+="int b;\n"
    ret_string+="INIT:\n"
    ret_string+="do\n"
    #  ret_string+="  :: true -> {\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="      b = len("+str(chan)+");\n"
    ret_string+="      do\n"
    ret_string+="      :: b != len("+str(chan)+") -> goto INIT;\n"
    ret_string+="      od\n"
    ret_string+="    }\n"
    ret_string+="  :: goto CONSUME;\n"
    ret_string+="od\n"
    ret_string+="CONSUME:\n"
    ret_string+="do\n"
    ret_string+="  :: "+str(chan)+" ? "+str(fs)+" -> atomic {\n"
    ret_string+="    "+str(attacker_mem)+" ! "+str(fs)+";\n"
    ret_string+="    do\n"
    ret_string+="    :: goto REPLAY;\n"
    ret_string+="    :: goto CONSUME;\n"
    ret_string+="    od\n"
    ret_string+="  }\n"
    ret_string+="od\n"
    ret_string+="REPLAY:\n"
    ret_string+="  do\n"
    ret_string+="  :: atomic {\n"
    ret_string+="  int am;\n"
    ret_string+="    select(am : 0 .. len("+str(attacker_mem)+")-1);\n"
    ret_string+="    do\n"
    ret_string+="    :: am != 0 -> \n"
    ret_string+="      am = am-1;\n"
    ret_string+="      "+str(attacker_mem)+" ? "+str(fs)+" -> "+str(attacker_mem)+" ! "+str(fs)+";\n"
    ret_string+="    :: am == 0 ->\n"
    ret_string+="      "+str(attacker_mem)+" ? "+str(fs)+" -> "+str(chan)+" ! "+str(fs)+";\n"
    ret_string+="      break;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: empty("+str(attacker_mem)+") -> goto BREAK;\n"
    ret_string+="  od\n"
    ret_string+="BREAK:\n"
    ret_string+="}\n"

    return ret_string

def gen_drop(chan : str, chan_type : List[str], mem : int, index : int) -> str:
    ret_string = ""

    ret_string+= "active proctype attacker_drop_"+str(index)+"() {\n"

    # proctype variables
    item_arr = []
    item_count = 0


    # formulate string of general message input variables
    for item in chan_type:
        item_arr.append("b_" + str(item_count))
        ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        item_count+=1

    fs = (str([item for item in item_arr])[1:-1]).replace("'","")

    ret_string+="byte i = "+str(mem)+";\n"
    ret_string+="int b;\n"
    ret_string+="MAIN:\n"
    ret_string+="  do\n"
    ret_string+="  :: "+str(chan)+" ? ["+fs+"] -> atomic {\n"
    ret_string+="    if\n"
    ret_string+="    :: i == 0 -> goto BREAK;\n"
    ret_string+="    :: else ->\n"
    ret_string+="      "+str(chan)+" ? "+fs+";\n"
    ret_string+="       i = i - 1;\n"
    ret_string+="       goto MAIN;\n"
    ret_string+="    fi\n"
    ret_string+="    }\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto MAIN;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: goto BREAK;\n"
    ret_string+="  od\n"
    ret_string+="BREAK:\n"
    ret_string+="}\n"

    return ret_string

def gen_drop_unbounded(chan : str, chan_type : List[str], index : int) -> str:
    ret_string = ""

    ret_string+= "active proctype attacker_drop_"+str(index)+"() {\n"

    # proctype variables
    item_arr = []
    item_count = 0

    # formulate string of general message input variables
    for item in chan_type:
        item_arr.append("b_" + str(item_count))
        ret_string+= str(item) + " " + item_arr[item_count] + ";\n"
        item_count+=1

    fs = (str([item for item in item_arr])[1:-1]).replace("'","")

    ret_string+="int b;\n"
    ret_string+="MAIN:\n"
    ret_string+="  do\n"
    ret_string+="  :: "+str(chan)+" ? ["+fs+"] -> atomic {\n"
    ret_string+="    do \n"
    ret_string+="    :: goto BREAK;\n"
    ret_string+="    :: true ->\n"
    ret_string+="      "+str(chan)+" ? "+fs+";\n"
    ret_string+="       goto MAIN;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: "+str(chan)+" ? ["+str(fs)+"] -> {\n"
    ret_string+="    b = len("+str(chan)+");\n"
    ret_string+="    do\n"
    ret_string+="    :: b != len("+str(chan)+") -> goto MAIN;\n"
    ret_string+="    od\n"
    ret_string+="    }\n"
    ret_string+="  :: goto BREAK;\n"
    ret_string+="  od\n"
    ret_string+="BREAK:\n"
    ret_string+="}\n"

    return ret_string
