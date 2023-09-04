import json
import os
from core.GenConstr import *


def GenModel():
    path = os.path.abspath(__file__)
    path = path[:len(path) - 11] + "model/"
    # print(path)
    rn_path = path + "rn.json"
    gn_path = path + "gn.json"
    # ----------------- Road Network -----------------
    map_dict = {}
    f = open(rn_path, 'r')
    rn_data = json.load(f)
    m = len(rn_data['region'])
    # make a spatial table
    p_table = [None] * (m + 1)
    for i in range(len(p_table)):
        p_table[i] = [0] * m
    number = 0
    for i in rn_data['region']:
        map_dict[i['key']] = int(i['id'])
        p_table[0][number] = int(i['id'])
        p = 0
        list_s = i['spatial-relation'].replace(" ", "").split(",")
        for j in list_s:
            p_table[number + 1][p] = GetInt(j)
            p = p + 1
        number = number + 1
    f.close()
    f = open(gn_path, 'r')
    data = json.load(f)
    # ----------------- Grid Network -----------------
    m = len(data['region'])
    # make a mapping to RoadNetwork
    mrn = [None] * 3
    # make a spatial table
    stable = [None] * (m+2)
    # make a free table
    free = [None] * 2
    for i in range(len(stable)):
        stable[i] = [0] * m
    for i in range(len(free)):
        free[i] = [0] * m
    for i in range(len(mrn)):
        mrn[i] = [0] * m
    number = 0
    index_dict = {"0": 0}
    for i in data['region']:
        stable[0][number] = int(i['id'])
        stable[m+1][number] = map_dict[i['f_key']]
        mrn[0][number] = int(i['id'])
        mrn[1][number] = GetRorC(i['f_key'])
        mrn[2][number] = int(i['f_key'][2:])
        index_dict[i['id']] = number
        free[0][number] = int(i['id'])
        free[1][number] = int(i['free'])
        p = 0
        list_s = i['spatial-relation'].replace(" ", "").split(",")
        for j in list_s:
            stable[number + 1][p] = GetInt(j)
            p = p + 1
        number = number + 1

    n = len(data['object'])
    reserve = [None] * (m+1)
    claim = [None] * (m+1)
    dire = [None] * 2
    speed = [None] * 2
    left = [None] * 2
    right = [None] * 2
    acc = [None] * 2
    path = [None] * n
    for i in range(len(reserve)):
        reserve[i] = [0] * n
        claim[i] = [0] * n
    for i in range(len(dire)):
        dire[i] = [0] * n
        speed[i] = [0] * n
        left[i] = [0] * n
        right[i] = [0] * n
        acc[i] = [0] * n
    for i in range(len(path)):
        path[i] = [0] * 4

    number = 0
    object_dict = {}
    for i in data['object']:
        object_dict[i['id']] = number
        reserve[0][number] = int(i['id'])
        claim[0][number] = int(i['id'])
        dire[0][number] = int(i['id'])
        speed[0][number] = int(i['id'])
        left[0][number] = int(i['id'])
        right[0][number] = int(i['id'])
        acc[0][number] = int(i['id'])
        reserve[index_dict[i['pos']] + 1][number] = 1
        if i['cl'] != "":
            list_s = i['cl'].replace(" ", "").split(",")
            for j in list_s:
                claim[index_dict[j] + 1][number] = 1
        dire[1][number] = int(GetInt(i['dir']))
        speed[1][number] = int(i['spd'])
        left[1][number] = int(i['left'])
        right[1][number] = int(i['right'])
        acc[1][number] = int(i['acc'])
        list_s = i['path'].replace(" ", "").split(",")
        p = 0
        for j in list_s:
            path[number][p] = index_dict[j]
            p = p + 1
        number = number + 1
    f.close()
    model = {0: stable, 1: reserve, 2: claim, 3: free, 4: path, 5: dire, 6: speed, 7: left, 8: right, 9: acc, 10: mrn, 11: p_table}
    # print(model)
    return model, m, index_dict, object_dict

if __name__ == '__main__':
    GenModel()
