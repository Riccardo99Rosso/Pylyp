#!/usr/bin/env python3

import sys
import ast
import symtable
import os

additional_args = []

compiler_commands = ["-d", "-debug", "-v", "-visualize"]
#comments on errors
comments = False
#tree visualizer
visualize = False

def print_instructions():
    print("usage: pylyp [code.py] [options]")
    print("options:")
    print("-debug (or -d):      " + "Show errors on non-reversible instructions")
    print("-visualize (or -v):  " + "Show the AST")
    print("Using 'pylyp' command without any code or options is the equivalent")
    print("of calling the 'python' command")

l = len(sys.argv)

if l == 1:
    print("ciao")
    cmd = f'start cmd.exe @cmd /k python'
    os.system(cmd)
    
else:
    firstarg = (sys.argv[1])

    if l > 2:
        i = 2
        while(i < l):
            if sys.argv[i] in compiler_commands:
                if sys.argv[i] == "-d" or sys.argv[i] == "-debug":
                    comments = True
                elif sys.argv[i] == "-v" or sys.argv[i] == "-visualize":
                    visualize = True
                else:
                    print("Unexpected error in additional arguments!")
            else:
                print_instructions()
            i += 1

    f = open(firstarg, "r")
    code = f.read()
       
    #list of accepted functions
    rev_functions = ["range"]

    tree_ast = ast.parse(code, mode="exec")

    st1 = symtable.symtable(code, 'sym_table', 'exec')
    sub_st1 = st1.get_children()
    fun_size = 0
    is_reversible_symtable = []
    for child in range(len(sub_st1)):
        if str(sub_st1[child].get_type()) == 'function':
            st2 = sub_st1[child]
            global_list = list(st2.get_globals())
            for f in rev_functions:
                if f in global_list:
                    global_list.remove(f)
            if global_list:
                is_reversible_symtable.append(False)
                if comments:
                    print("Function \"" + sub_st1[child].get_name() + "\" is not closed")
            else:
                is_reversible_symtable.append(True)
            fun_size += 1

    fun_count = 0
    super_nodes = [node for node in ast.walk(tree_ast)]
    print()
    print("---")
    for super_n in super_nodes:
        if isinstance(super_n, ast.FunctionDef):
            is_reversible = True
            nodes = [node for node in ast.walk(super_n)]
            for n in nodes:                
                if isinstance(n, ast.Assign):
                    subNodes = [node for node in ast.walk(n.value)]
                    for target in n.targets:
                        if not isinstance(target, ast.Name):
                            if comments:
                                print("At line: ", target.lineno)
                                print("Multiple assignment is not allowed\n")
                            is_reversible = False
                    for sub_n in subNodes:
                        try:
                            if not isinstance(sub_n, ast.Constant):
                                if isinstance(sub_n, ast.BinOp):
                                    if sub_n.left.id != target.id:
                                        if comments:
                                            print("At line: ", n.lineno)
                                            print("This type of assignment is not allowed\n")
                                        is_reversible = False
                                        break
                                    elif not(isinstance(sub_n.op, ast.Add) or isinstance(sub_n.op, ast.Sub)):
                                        if comments:
                                            print("At line: ", n.lineno)
                                            print("This type of assignment is not allowed\n")
                                        is_reversible = False
                                        break
                                    elif sub_n.right.value != 1:
                                        if comments:
                                            print("At line: ", n.lineno)
                                            print("This type of assignment is not allowed\n")
                                        is_reversible = False
                                        break
                        except:
                            if comments:
                                print("At line: ", n.lineno)
                                print("This type of assignment is not allowed\n")
                            is_reversible = False
                if isinstance(n, ast.AugAssign):
                    subNodes = [node for node in ast.walk(n)]
                    div_or_mult = False
                    for sub_n in subNodes:
                        if isinstance(sub_n, ast.Mult):
                            if comments:
                                print("At line: ", n.lineno)
                                print("*= is not allowed\n")
                            div_or_mult = True
                            is_reversible = False
                        if isinstance(sub_n, ast.Div):
                            if comments:
                                print("At line: ", n.lineno)
                                print("/= is not allowed\n")
                            div_or_mult = True
                            is_reversible = False
                    if(not div_or_mult):
                        subNodes = [node for node in ast.walk(n.value)]
                        done = False
                        for sub_n in subNodes:
                            if isinstance(sub_n, ast.Name):
                                if comments:
                                    print("At line: ", n.lineno)
                                    print("There is a variable in the right part of the augmented assignment\n")
                                done = True
                                is_reversible = False
                        if(not done):
                            tmp_tree = ast.dump(n.value)
                            val = str(tmp_tree)
                            if val.count("value=") != 1:
                                if comments:
                                    print("At line: ", n.lineno)
                                    print("The value of the augmented assignment must be only one\n")
                                is_reversible = False
                            else:
                                if (not "value=1" in val) or ("op=USub()" in val):
                                    if comments:
                                        print("At line: ", n.lineno)
                                        print("The value of the augmented assignment must be '1'\n")
                                    is_reversible = False
                if isinstance(n, ast.While):
                    if comments:
                        print("At line: ", n.lineno)
                        print("The while loop is not reversible")
                    is_reversible = False
                if isinstance(n, ast.IfExp):
                    if comments:
                        print("At line: ", n.lineno)
                        print("This type of construct is not allowed, please use the standard if else construct\n")
                    is_reversible = False
                if isinstance(n, ast.If):
                    cond_var = []
                    bodyelse_var = []
                    tmp_tree = ast.dump(n.test)
                    strp = str(tmp_tree)
                    strp_save = strp
                    while "id='" in strp:
                        strp = strp.split("id='",1)[1]
                        cond_var.append(strp)
                    count = 0
                    for s in cond_var:
                        s = cond_var[count]
                        x = str(s)
                        x = x.partition("'")[0]
                        cond_var[count] = x
                        count += 1
                    cond_var = list(set(cond_var))
                    subNodes = [node for node in ast.walk(n)]
                    for sub_n in subNodes:
                        if isinstance(sub_n, ast.Assign):
                            for target in sub_n.targets:
                                bodyelse_var.append(target.id)
                        if isinstance(sub_n, ast.AugAssign):
                                bodyelse_var.append(sub_n.target.id)
                    bodyelse_var = list(set(bodyelse_var))
                    intersect = list(set(bodyelse_var).intersection(cond_var))
                    if intersect:
                        if comments:
                            print("At line: ", n.lineno)
                            print("The variables inside the condition of the if statement are changed in the body\nor in the body of the else\n")
                        is_reversible = False
                if isinstance(n, ast.For):
                    cond_var = []
                    bodyelse_var = []
                    tmp_tree = ast.dump(n.target)
                    strp = str(tmp_tree)
                    strp_save = strp
                    while "id='" in strp:
                        strp = strp.split("id='",1)[1]
                        cond_var.append(strp)
                    count = 0
                    for s in cond_var:
                        s = cond_var[count]
                        x = str(s)
                        x = x.partition("'")[0]
                        cond_var[count] = x
                        count += 1
                    if isinstance(n.iter, ast.Name):
                        cond_var.append(n.iter.id)
                    cond_var = list(set(cond_var))
                    subNodes = [node for node in ast.walk(n)]
                    for sub_n in subNodes:
                        if isinstance(sub_n, ast.Assign):
                            for target in sub_n.targets:
                                bodyelse_var.append(target.id)
                        if isinstance(sub_n, ast.AugAssign):
                                bodyelse_var.append(sub_n.target.id)
                    bodyelse_var = list(set(bodyelse_var))
                    intersect = list(set(bodyelse_var).intersection(cond_var))
                    if intersect:
                        if comments:
                            print("At line: ", n.lineno)
                            print("The target variable or the iter variable of the for statement is changed in the body\nor in the body of the else\n")
                        is_reversible = False
            is_reversible  = is_reversible and is_reversible_symtable[fun_count]              
            print("Function:", super_n.name,", reversibility: ", is_reversible)
            print("-")
            fun_count += 1
    print("---")
    print()
    tree = ast.dump(tree_ast, indent=4)
    if visualize:
        print("---")
        print(tree)
        print("---\n")
    
    output = compile(tree_ast, sys.argv[1],'exec')
    exec(output)
