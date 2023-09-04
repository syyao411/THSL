import re

from core.GenConstr import *


def indexStr(sn, s):
    # Returns the index of all required
    res = []
    for i in range(sn.count(s)):
        if i == 0:
            pos = sn.index(s)
        else:
            pos = sn.index(s, pos + 1)
        res.append(pos)
    return res


def splitStr(s):
    # A simplified process for syntax checking:
    #   1、Split by blank
    #   2、Split parenthesis
    #   3、Process keyword
    # /**
    #     Test Case:
    #     ((~re(a3) (F|B) re(b)))
    #     (~(re(a3) (F|B) re(b)))
    #     ((~re(a3) ~(F|B) re(b)))
    #     ((~re(a3) ~F re(b)))
    #     ~(re(a) F ((cross And ~cl(a))) And re(a) F free)
    #     ((~re(a3) (F|B) re(b)))
    #     re(a) F free F cross And re(a) LF re(a1)
    #     re(a) F ((cross And ~cl(a))) And re(a) F free
    # **/
    #   1、Split by blank
    pre = s.split(" ")
    # print(pre)
    res = []
    #   2、Split parenthesis
    for item in pre:
        if item is not "(" and len(indexStr(item, "(")) > len(indexStr(item, ")")):
            list_i = indexStr(item, "(")
            j = 0
            if len(indexStr(item, ")")) == 0:
                for i in range(len(list_i)):
                    res.append(item[j:list_i[i] + 1])
                    j = list_i[i] + 1
                res.append(item[j:])
            else:
                for i in range(len(list_i) - 1):
                    if list_i[i] == list_i[i + 1] - 1:
                        res.append(item[j:list_i[i] + 1])
                        j = list_i[i] + 1
                    else:
                        res.append(item[j:list_i[i] + 1])
                        j = list_i[i] + 1

                    if i == len(list_i) - 2:
                        res.append(item[j:])
        elif item is not ")" and len(indexStr(item, ")")) > len(indexStr(item, "(")):
            list_i = indexStr(item, ")")
            if len(indexStr(item, "(")) == 0:
                for i in range(len(list_i)):
                    if i == 0:
                        res.append(item[:list_i[i]])
                        res.append(item[list_i[i]:list_i[i] + 1])
                    else:
                        res.append(item[list_i[i]:list_i[i] + 1])
            else:
                for i in range(len(list_i) - 1):
                    if i == 0:
                        res.append(item[:list_i[i] + 1])
                        res.append(item[list_i[i] + 1:list_i[i + 1] + 1])
                    else:
                        res.append(item[list_i[i] + 1:list_i[i + 1] + 1])
        else:
            res.append(item)
    #   3、Process keyword
    rest = []
    for item in res:
        # use below mode to pattern the multi-spatial operation
        # re.match(r"^([~]*[(F|B|L|R|LF|LB|RF|RB)|]+)+([~]*[F|B|L|R|LF|LB|RF|RB])$", item)
        if len(indexStr(item, "~")) > 0 and re.match(r"^[~]*\([(F|B|L|R|LF|LB|RF|RB)|]+(F|B|L|R|LF|LB|RF|RB)\)$", item) is None and re.match(r"^[~]*(F|B|L|R|LF|LB|RF|RB)$", item) is None:
            list_i = indexStr(item, "~")
            j = 0
            for i in range(len(list_i)):
                rest.append(item[j:list_i[i] + 1])
                j = list_i[i] + 1
            rest.append(item[j:])
        else:
            rest.append(item)
    return rest


def strCheck(s):
    for item in s:
        if item == "(" or item == ")" or item == "And" or item == "Or":
            return "True"
            # print(1)
        elif re.match(r"^[~]*(F|B|L|R|LF|LB|RF|RB)$", item) is not None:
            return "True"
            # print(2)
        # use below mode to pattern the multi-spatial operation
        # re.match(r"^([~]*[(F|B|L|R|LF|LB|RF|RB)|]+)+([~]*[F|B|L|R|LF|LB|RF|RB])$", item)
        elif re.match(r"^[~]*\([(F|B|L|R|LF|LB|RF|RB)|]+(F|B|L|R|LF|LB|RF|RB)\)$", item) is not None:
            return "True"
            # print(3)
        elif re.match(r"^re\([a-z]{1}[0-9]{0,1}\)$", item) is not None:
            return "True"
            # print(4)
        elif re.match(r"^cl\([a-z]{1}[0-9]{0,1}\)$", item) is not None:
            return "True"
            # print(5)
        elif re.match(r"^free$", item) is not None or re.match(r"^cross$", item) is not None:
            return "True"
            # print(6)
        elif re.match(r"^~$", item) is not None:
            return "True"
            # print(7)
        else:
            return item
    return "True"


if __name__ == '__main__':
    string = input('Please input a string:')
    if re.match(r"^([~]*[(F|B|L|R|LF|LB|RF|RB)|]+)+([~]*[F|B|L|R|LF|LB|RF|RB])$", string) is not None:
        so_list = string.split("|")
        temp = ""
        for so_item in so_list:
            temp = temp + GetStr(GetAbsolute(GetSoTrue(so_item), 1)) + "|"
        print("The new node.val is:" + temp[:len(temp) - 1])
    else:
        print(0)
    # result = splitStr(string)
    # print(result)
    # if strCheck(result) is not "True":
    #     print("There may be a error occur at " + strCheck(result) + " in syntax \"" + string + "\"")
    # else:
    #     print(result)
