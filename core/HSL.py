import queue
from core.GenConstr import *
from core.GenModel import *
from core.Gtreex import *
from core.Scheckx import *
# import datetime
import time

# (re(a1) B cl(a2)) And (re(a1) RB re(a2))
# (re(a1) B re(a2)) And (re(a1) RB re(a2))
# (re(a1) B re(a2)) Or (re(a1) RB re(a2))
# 1,1,1,1,1,1,1,1
# 1-8 ::= E,ES,S,WS,W,WN,N,EN
# re(a1) B cl(a2) RB re(a2) , 101 , 0,0,0,1,0,0,1,1
# re(a2) RF cl(a2) F cross LF free , 103 , 0,0,0,0,1,1,1,1


def input_hsl(a, b, c):
    model, len_region, region_dict, object_dict = GenModel()
    # formula = input('Please input the formula:')
    # vehicle = input('Please input the id of host vehicle:')
    # view = input('Please input the observed view:')
    formula = a
    vehicle = b
    view = c
    first_region = ""
    first_vehicle = ""
    for key, _ in region_dict.items():
        first_region = key
        break
    for key, _ in object_dict.items():
        first_vehicle = key
        break
    # check vehicle
    if vehicle not in object_dict:
        print("invalid input of vehicle")
        return "0", "0", "0", "0"
    # check view
    constr_first = view.replace(" ", "").split(",")
    if len(constr_first) != len_region:
        print("invalid input of view")
        return "0", "0", "0", "0"
    else:
        for i in constr_first:
            if i != "0" and i != "1":
                print("invalid input of view")
                return "0", "0", "0", "0"
    return model, formula, vehicle, constr_first, len_region, first_region, first_vehicle


def hsl_sat(a, b, c):
    model, in_formula, host_vehicle, view, len_region, first_region, first_vehicle = input_hsl(a, b, c)
    if in_formula == "0":
        return
    formula = splitStr(in_formula)
    # print(formula)
    # Check whether the formula $\psi$ is syntactic.
    if strCheck(formula) is not "True":
        print("invalid formula")
    else:
        sol = Solution()
        # Converts formula $\psi$ into a binary syntax tree.
        root = sol.InExpTree(formula)
        root, len_tree = levelTree(root)
        # print(len_region + 1)
        # print(model[1])
        # print(model[2])
        # the 5 needs to be replaced by len_region + 1
        draw_tree(root)
        res = [[Int('x_%d_%d' % (i + 1, j + 1)) for j in range(len_region + 1)] for i in range(len_tree)]
        # Obtain the observed view of host vehicle,
        # transform the relative direction and absolute direction.
        direction = model[5]
        dir_host = direction[1][int(host_vehicle) - 100]
        # the 101 needs to be replaced by int(first_vehicle)
        # print("The direction of vehicle is:" + str(dir_host))
        # Add the first constraint for the initial viewing area
        pre = time.perf_counter()
        constr_list = []
        constr = [And([res[1][i+1] == int(view[i]) for i in range(len_region)])]
        # constr = [And(res[1][1] == 0, res[1][2] == 1, res[1][3] == 1, res[1][4] == 1)]
        constr_list.append(constr)
        queue_l = queue.Queue()
        queue_l.put(root)
        while not queue_l.empty():
            node = queue_l.get()
            # print("Using marked sign 1:" + str(node.id))
            # print("node.info is:" + node.info)
            # print("node.val is:" + node.val)
            # rewrite it as
            # if re.match(r"^([~]*[(F|B|L|R|LF|LB|RF|RB)|]+)+([~]*[F|B|L|R|LF|LB|RF|RB])$", node.val) is not None:
            #     so_list = node.val.split("|")
            #     temp = ""
            #     for so_item in so_list:
            #         temp = temp + GetStr(GetAbsolute(GetSoTrue(so_item), dir_host)) + "|"
            #     print("The new node.val is:" + temp[:len(temp) - 1])
            if re.match(r"^[~]*(F|B|L|R|LF|LB|RF|RB)$", node.val) is not None:
                node.nval = GetStr(GetAbsolute(node.val, dir_host))
                # print("The new node.val is:" + node.nval)
            # Generate constraints on node, the pseudo code is covered in Algorithms 2.
            constr = GenConstr(model, res, node, 1)
            # print(constr)
            count = len(constr)
            for item in constr:
                constr_list.append(item)
            # Set a z3 solver.
            s = Solver()
            for item in constr_list:
                s.add(item)
            # Use SMT solver to determine whether $res$ has a feasible solution within limitaion $constr\_list$.
            if s.check() == unsat:
                while count > 0:
                    constr_list.pop()
                    count = count - 1
                # print("Using marked sign 0:" + str(node.id))
                constr = GenConstr(model, res, node, 0)
                constr_list.append(constr[0])
            else:
                if node.left:
                    queue_l.put(node.left)
                if node.right:
                    queue_l.put(node.right)
        cur = time.perf_counter()
        s = Solver()
        for item in constr_list:
            s.add(item)
        if s.check() == sat:
            m = s.model()
            res_truth = ""
            res_info = ""
            if res[0][0] == 0:
                # print("unsat")
                res_truth = "False"
            else:
                res_truth = "True"
                r = [[m.evaluate(res[i][j]) for j in range(len_region + 1)]
                     for i in range(len_tree)]
                q = [[m.evaluate(res[i][j]) for j in range(len_region + 1)]
                     for i in range(1, len_tree)]
                # print_matrix(q)
                col = len(r[0])
                info_queue = queue.Queue()
                info_queue.put(root)
                while not info_queue.empty():
                    node = info_queue.get()
                    if r[node.id][0] == 1:
                        # print("The formula under node " + node.val + "(" + node.info + ") holds for region [ ", end="")
                        res_info = res_info + "The formula under node " + node.val + "(" + node.info + ") holds for region [ "
                        for j in range(col):
                            if j != 0 and r[node.id][j] == 1:
                                # print(str(j) + " ", end="")
                                res_info = res_info + str(j) + " "
                        # print("]")
                        res_info = res_info + "]\n"
                    else:
                        # print("The formula under node " + node.val + "(" + node.info + ") does not hold")
                        res_info = res_info + "The formula under node " + node.val + "(" + node.info + ") does not hold\n"
                    if node.left:
                        info_queue.put(node.left)
                    if node.right:
                        info_queue.put(node.right)
            cal_time = round((cur - pre) * 1000, 2)
            return res_truth, res_info, str(cal_time) + "ms"


if __name__ == '__main__':
    hsl_sat()
