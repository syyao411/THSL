import graphviz
from core.Scheckx import *


class TNode:
    def __init__(self, x):
        self.val = x
        self.id = None
        self.left = None
        self.right = None
        self.info = ""
        self.nval = ""


class Solution:
    # Determine whether it is an operator
    def isOper(self, ch):
        if ch == "(" or ch == ")" or ch == "And" or ch == "Or":
            return True
        elif ch == "~":
            return True
        elif re.match(r"^[~]*\([(F|B|L|R|LF|LB|RF|RB)|]+(F|B|L|R|LF|LB|RF|RB)\)$", ch) is not None or re.match(r"^[~]*(F|B|L|R|LF|LB|RF|RB)$", ch) is not None:
            return True
        return False

    # Gets the priority level corresponding to the operator
    def getOperOrder(self, ch):
        if ch == '(':
            return 1
        if ch in ['And', 'Or']:
            return 2
        if re.match(r"^[~]*\([(F|B|L|R|LF|LB|RF|RB)|]+(F|B|L|R|LF|LB|RF|RB)\)$", ch) is not None or re.match(r"^[~]*(F|B|L|R|LF|LB|RF|RB)$", ch) is not None:
            return 3
        if ch == "~":
            return 4
        return 0

    # In order expression generates a binary tree
    def InorderTree(self, pNode):
        if not pNode:
            return
        if pNode.left:
            # Parentheses are required if the left subtree is a symbolic and it's priority lower than parent's
            if self.isOper(pNode.left.val) and self.getOperOrder(pNode.left.val) < self.getOperOrder(pNode.val):
                res.append('(')
                self.InorderTree(pNode.left)
                res.append(')')
            else:
                self.InorderTree(pNode.left)
        res.append(pNode.val)
        if pNode.right:
            # Parentheses are required if the right subtree is a symbolic and it's priority lower than parent's
            if self.isOper(pNode.right.val) and self.getOperOrder(pNode.right.val) <= self.getOperOrder(pNode.val):
                res.append('(')
                self.InorderTree(pNode.right)
                res.append(')')
            else:
                self.InorderTree(pNode.right)

    # Create a binary tree
    def createTree(self, data):
        if not data:
            return
        ch = data.pop(0)
        if ch == '#':
            return None
        else:
            root = TNode(ch)
            root.left = self.createTree(data)
            root.right = self.createTree(data)
            return root

    # Post expression generates a binary tree
    def PostExpTree(self, data):
        if not data:
            return
        rep = []
        while data:
            tmp = data.pop(0)
            if not self.isOper(tmp):
                if tmp.find('(') != -1:
                    p = TNode(tmp)
                    pos = tmp.find('(')
                    p.val = tmp[0:pos]
                    p.info = tmp[pos + 1:len(tmp) - 1]
                    rep.append(p)
                else:
                    p = TNode(tmp)
                    p.val = tmp
                    p.info = tmp
                    rep.append(p)
            elif self.getOperOrder(tmp) == 4:
                p = TNode(tmp)
                p.left = rep.pop()
                p.right = None
                p.info = "Not"
                rep.append(p)
            else:
                p = TNode(tmp)
                p.right = rep.pop()
                p.left = rep.pop()
                if self.getOperOrder(tmp) == 3:
                    p.info = "spatial"
                if self.getOperOrder(tmp) == 2:
                    p.info = "common"
                rep.append(p)
        return rep.pop()

    # Prefix expression generates a binary tree
    def PreExpTree(self, data):
        rep = []
        while data:
            tmp = data.pop()
            if not self.isOper(tmp):
                rep.append(TNode(tmp))
            elif self.getOperOrder(tmp) == 4:
                p = TNode(tmp)
                p.left = rep.pop()
                p.right = None
                rep.append(p)
            else:
                p = TNode(tmp)
                p.left = rep.pop()
                p.right = rep.pop()
                rep.append(p)
        return rep.pop()

    # In order expression generates a binary tree
    def InExpTree(self, data):
        rep = []
        op = []
        while data:
            tmp = data.pop(0)
            if not self.isOper(tmp):
                rep.append(tmp)
            else:
                if tmp == '(':
                    op.append('(')
                elif tmp == ')':
                    while op[-1] != '(':
                        rep.append(op.pop())
                    op.pop()
                elif re.match(r"^[~]*\([(F|B|L|R|LF|LB|RF|RB)|]+(F|B|L|R|LF|LB|RF|RB)\)$", tmp) is not None or re.match(r"^[~]*(F|B|L|R|LF|LB|RF|RB)$", tmp) is not None or tmp == "And" or tmp == "Or" or tmp == "~":
                    while op and op[-1] != '(' and self.getOperOrder(op[-1]) >= self.getOperOrder(tmp):
                        rep.append(op.pop())
                    op.append(tmp)
        if op:
            rep = rep + op[::-1]
        # print(rep)
        return self.PostExpTree(rep)


# The sequence traverses the tree, marking the nodes in order
def levelTree(root):
    if not root:
        return
    queue = [root]
    i = 1
    while queue:
        node = queue.pop(0)
        node.id = i
        i = i + 1
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return root, i


# Prefix order recursively traverses each node,
# using the unique id generated by levelTree as the node number
# and val as the label value to draw tree
def tree_to_dot(root, dot):
    if not root:
        return
    dot.node(str(root.id), label=str(root.val + "(" + root.info + ")"))
    if root.left:
        dot.edge(str(root.id), str(root.left.id))
        tree_to_dot(root.left, dot)
    if root.right:
        dot.edge(str(root.id), str(root.right.id))
        tree_to_dot(root.right, dot)


# Create a dot file and save it to the img folder named tree.png
def draw_tree(root):
    dot = graphviz.Digraph(comment='Binary Tree')
    tree_to_dot(root, dot)
    dot.format = 'svg'
    dot.render('tree', './img')


def isLeaf(root):
    if not root.left and not root.right:
        return True
    return False


# /** Addition info:
#       层序遍历的方式将生成的语法树划分为非叶子节点列表nodeList和叶子结点列表leafList
#       同时给出对应的nodeList映射到的子节点的下标
# **/
def con_tree_list(root):
    if not root:
        return
    queue = [root]
    nodelist = {}
    nodeindex = {}
    leaflist = {}
    leaf = []
    while queue:
        size = len(queue)
        for _ in range(size):
            node = queue.pop(0)
            if node.left and node.right:
                nodeindex[node.id] = {
                        'left': node.left.id,
                        'right': node.right.id
                }
                if Solution.getOperOrder(node.val, node.val) == 2 and node.val == "Or":
                    nodelist[node.id] = {
                        'type_x': 1,
                        'value': node.val,
                        'left': node.left.id,
                        'right': node.right.id}
                elif Solution.getOperOrder(node.val, node.val) == 2 and node.val == "And":
                    nodelist[node.id] = {
                        'type_x': 2,
                        'value': node.val,
                        'left': node.left.id,
                        'right': node.right.id}
                elif Solution.getOperOrder(node.val, node.val) == 3:
                    nodelist[node.id] = {
                        'type_x': 3,
                        'value': node.val,
                        'left': node.left.id,
                        'right': node.right.id}
            elif node.left and not node.right:
                nodeindex[node.id] = {
                    'left': node.left.id,
                    'right': -1
                }
                if Solution.getOperOrder(node.val, node.val) == 4:
                    nodelist[node.id] = {
                        'type_x': 0,
                        'value': node.val,
                        'left': node.left.id,
                        'right': -1}
            else:
                m = ""
                x = ""
                if "free" in node.val:
                    m = "free"
                elif "cl" in node.val:
                    m = "cl"
                    x = re.findall(r'\((.*?)\)', node.val)[0]
                elif "re" in node.val:
                    m = "re"
                    x = re.findall(r'\((.*?)\)', node.val)[0]
                elif "cross" in node.val:
                    m = "cross"
                if "~" in node.val:
                    n = 0
                else:
                    n = 1
                leaflist[node.id] = {
                    'type_x': m,
                    'value': x,
                    'truth': n}
                leaf.append(node.id)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return nodelist, leaflist, nodeindex, leaf


if __name__ == '__main__':
    string = input('请输入一个字符串:')
    result = splitStr(string)
    print(result)
    if strCheck(result) is not "True":
        print("There may be a error occur at " + strCheck(result) + " in syntax \"" + string + "\"")
    else:
        print(result)
        s = Solution()
        t1 = s.InExpTree(result)
        t1 = levelTree(t1)
        nodelist, leaflist, nodeindex, leaf = con_tree_list(t1)
        res = []
        draw_tree(t1)
        s.InorderTree(t1)
        res = map(str, res)
        print(''.join(res))
        print(nodelist)
        print(leaflist)
        print(nodeindex)
        leaf = map(str, leaf)
        print("["+','.join(leaf)+"]")
