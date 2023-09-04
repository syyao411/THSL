from core.Gtreex import *
from z3 import *


def GenConstr(model, res, node, p):
    size = len(res[0]) - 1
    constr = []
    if p == 0:
        constr.append([res[node.id][0] == 0])
    elif p == 1:
        if isLeaf(node):
            # Mark the leaf node is True
            constr.append([res[node.id][0] == 1])
            # Add a constraint on the row of node's id that only one region can be selected from range 1 to n.
            constr.append([And([Implies(And(res[node.id][j+1] == 1, i != j), res[node.id][i+1] == 0)
                                for i in range(size) for j in range(size)])])
            # Add more information to obtain the node's label information
            if node.val == 'free':
                free = model[3]
                constr.append([Or([And(res[node.id][i + 1] == 1, free[1][i] == 1) for i in range(size)])])
            elif node.val == 'cross':
                constr.append([True])
            else:
                temp = node.info
                p = re.findall(r'\d+', temp)
                q = int(p[0])
                # print("The number of id of vehicle is " + str(q))
                if node.val == 're':
                    reserve = model[1]
                    constr.append([Or([And(res[node.id][i + 1] == 1, reserve[i + 1][q] == 1) for i in range(size)])])
                elif node.val == 'cl':
                    claim = model[2]
                    constr.append([Or([And(res[node.id][i + 1] == 1, claim[i + 1][q] == 1) for i in range(size)])])
        else:
            if node.info == "common":
                # Add constraints for the rows of node's and children(node)'s id to ensure that
                # all children are consistent to parent node in columns 1 to n.
                constr.append([Or(And(res[node.id][i+1] == 1, Or(res[node.left.id][i+1] == 1,
                                                                 res[node.left.id][i+1] == 0,
                                                                 res[node.right.id][i+1] == 1,
                                                                 res[node.right.id][i+1] == 0)),
                                  And(res[node.id][i+1] == 0, res[node.left.id][i+1] == 0, res[node.right.id][i+1] == 0))
                               for i in range(size)])
            elif node.info == "spatial":
                # Add constraint for the row of node's and children(node)'s id to ensure that
                # only one child selects the region as parent node selected in columns 1 to n,
                # and that all children are consistent to parent node unselected in columns 1 to n.
                constr.append([Or(And(res[node.id][i+1] == 1, res[node.left.id][i+1] == 1, res[node.right.id][i+1] == 0),
                               And(res[node.id][i+1] == 1, res[node.left.id][i+1] == 0, res[node.right.id][i+1] == 1),
                                  And(res[node.id][i+1] == 0, res[node.left.id][i+1] == 0, res[node.right.id][i+1] == 0))
                               for i in range(size)])
                stable = model[0]
                p = GetInt(node.nval)
                # split the node.val into multi-spatial operation
                # temp = node.val
                # so_list = temp.split("|")
                # for so_item in so_list:
                #     p = GetInt(so_item)
                #     print("The number of spatial direction is :" + str(p))
                #     constr.append([Or([And(res[node.left.id][i + 1] == 1, res[node.right.id][j + 1] == 1,
                #                            stable[i + 1][j] == p) for j in range(size) for i in range(size)])])
                # Add a constraint to ensure that the partition of regions
                # satisfies the spatial relationship hold by node.
                constr.append([Or([And(res[node.left.id][i+1] == 1, res[node.right.id][j+1] == 1, stable[i + 1][j] == p)
                               for j in range(size) for i in range(size)])])
            elif node.info in "Not":
                constr.append([Or(And(res[node.id][i + 1] == 1, res[node.left.id][i + 1] == 1),
                                  And(res[node.id][i + 1] == 0, res[node.left.id][i + 1] == 0))
                               for i in range(size)])
            if node.val == "Not":
                constr.append([Or(And(res[node.id][0] == 1, res[node.left.id][0] == 0),
                               And(res[node.id][0] == 0, res[node.left.id][0] == 1))])
            elif node.val == "Or":
                constr.append([Or(And(res[node.id][0] == 1, Or(res[node.left.id][0] == 1, res[node.right.id][0] == 1)),
                               And(res[node.id][0] == 0, And(res[node.left.id][0] == 0, res[node.right.id][0] == 0)))])
            else:
                constr.append([Or(And(res[node.id][0] == 1, And(res[node.left.id][0] == 1, res[node.right.id][0] == 1)),
                               And(res[node.id][0] == 0, Or(res[node.left.id][0] == 0, res[node.right.id][0] == 0)))])
    return constr


# Returns the value of 1-8, 1-8 ::= E,ES,S,WS,W,WN,N,EN
def GetInt(a):
    if a == 'E':
        return 1
    if a == 'ES':
        return 2
    if a == 'S':
        return 3
    if a == 'WS':
        return 4
    if a == 'W':
        return 5
    if a == 'WN':
        return 6
    if a == 'N':
        return 7
    if a == 'EN':
        return 8
    return 0


def GetStr(a):
    if a == 1:
        return 'E'
    if a == 2:
        return 'ES'
    if a == 3:
        return 'S'
    if a == 4:
        return 'WS'
    if a == 5:
        return 'W'
    if a == 6:
        return 'WN'
    if a == 7:
        return 'N'
    if a == 8:
        return 'EN'
    return ''


def GetSoTrue(a):
    if a.find("~") == -1:
        return a
    else:
        if a[1:] == 'F':
            return 'B'
        if a[1:] == 'RF':
            return 'LB'
        if a[1:] == 'R':
            return 'L'
        if a[1:] == 'RB':
            return 'LF'
        if a[1:] == 'B':
            return 'F'
        if a[1:] == 'LB':
            return 'RF'
        if a[1:] == 'L':
            return 'R'
        if a[1:] == 'LF':
            return 'RB'
        return ''


def GetRorC(a):
    if a[:1] == "r":
        return 0
    if a[:1] == "c":
        return 1
    return -1


def GetAbsolute(val, dirv):
    if val == 'F':
        return dirv
    if val == 'B':
        if (dirv + 4) % 8 == 0:
            return 8
        else:
            return (dirv + 4) % 8
    if val == 'L':
        if (dirv + 6) % 8 == 0:
            return 8
        else:
            return (dirv + 6) % 8
    if val == 'R':
        if (dirv + 2) % 8 == 0:
            return 8
        else:
            return (dirv + 2) % 8
    if val == 'LF':
        if (dirv + 7) % 8 == 0:
            return 8
        else:
            return (dirv + 7) % 8
    if val == 'RF':
        if (dirv + 1) % 8 == 0:
            return 8
        else:
            return (dirv + 1) % 8
    if val == 'LB':
        if (dirv + 5) % 8 == 0:
            return 8
        else:
            return (dirv + 5) % 8
    if val == 'RB':
        if (dirv + 3) % 8 == 0:
            return 8
        else:
            return (dirv + 3) % 8
    return 0
