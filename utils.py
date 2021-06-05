import queue
import pygraphviz as pgv


def bdd_dump_dot(root, mng, idx2var, filename="bdd.dot"):
    node_idx = 0
    c = 0
    if mng.IsComplement(root):
        c = (c + 1) % 2
    graph_bdd = pgv.AGraph(strict=False, directed=True)
    node2idx = {}
    stack = queue.LifoQueue()
    stack.put(((c, root), None, None))
    graph_bdd.add_node(-1, label="True", style="filled", color="green")
    graph_bdd.add_node(-2, label="False", style="filled", color="green")
    while not stack.empty():
        current, predecessor, branch = stack.get()
        c, node = current
        if current not in node2idx and not mng.IsConstant(node):
            e = mng.E(node)
            t = mng.T(node)
            e_c = c
            t_c = c
            if mng.IsComplement(e): e_c = (e_c + 1) % 2
            if mng.IsComplement(t): t_c = (t_c + 1) % 2
            stack.put(((t_c,t), current, 1))
            stack.put(((e_c,e), current, 0))
            graph_bdd.add_node(node_idx, label=idx2var[node.NodeReadIndex()].serialize())
            if predecessor is not None:
                if branch == 1: graph_bdd.add_edge(node2idx[predecessor],node_idx, style="solid")
                else: graph_bdd.add_edge(node2idx[predecessor],node_idx, style="dashed")
            node2idx[current] = node_idx
            node_idx = node_idx + 1
        else:
            if predecessor is not None:
                if mng.IsConstant(node):
                    if c == 0:
                        curr_idx = -1
                    else:
                        curr_idx = -2
                else:
                    curr_idx = node2idx[current]

                if branch == 1:
                    graph_bdd.add_edge(node2idx[predecessor], curr_idx, style="solid")
                else:
                    graph_bdd.add_edge(node2idx[predecessor], curr_idx, style="dashed")
    graph_bdd.write(filename)