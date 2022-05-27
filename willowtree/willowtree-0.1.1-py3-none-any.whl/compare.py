from tree import Node, Tree

def tree_from_bipartitions(bipartitions, leafnames):
    root = Node(name='root')
    for name in leafnames:
        root.add_child(name=name)
    t = Tree(root=root)

    bipartitions.sort(key = lambda x: min(len(x[0]), len(x[1])))
    while len(bipartitions) > 0:
        s = bipartitions.pop(0)
        minClade = min(s, key = lambda x: len(x))
        LCA = t.find_LCA(minClade)
        sep_nodes = []
        for child in LCA.children:
            if child.is_leaf() and child.name in minClade:
                sep_nodes.append(child)
            else:
                if set([leaf.name for leaf in child.get_leaves()]).issubset(set(minClade)):
                    sep_nodes.append(child)
        LCA.resolve_polytomy(sep_nodes)
    return t

def bipartitions_from_tree(tree, rooted=True):
    leafnames = [leaf.name for leaf in tree.iter_leaves()]
    bipartitions = []
    for node in tree.iter_descendants():
        if rooted:
            if node.is_root():
                bipartitions.append(([leaf.name for leaf in node.children[0].get_leaves()], [leaf.name for leaf in node.children[1].get_leaves()]))
            elif not node.parent.is_root() and not node.is_leaf():
                descendants = [leaf.name for leaf in node.get_leaves()]
                bipartitions.append((descendants, [x for x in leafnames if x not in set(descendants)]))
        else:
            if not node.is_root() and not node.is_leaf():
                descendants = [leaf.name for leaf in node.get_leaves()]
                bipartitions.append((descendants, [x for x in leafnames if x not in set(descendants)]))
    return bipartitions, leafnames

def strict_consensus(t1, t2):
    b1, l1 = bipartitions_from_tree(t1)
    b2, l2 = bipartitions_from_tree(t2)
    shared_bipartitions = []
    for i in b1:
        for j in b2:
            if set(min(i, key = lambda x: len(x))) == set(min(j, key = lambda x: len(x))):
                shared_bipartitions.append(i)
                b2.remove(j)
                break
    t = tree_from_bipartitions(shared_bipartitions, l1)
    return t

def robinson_foulds(t1, t2, rooted=True):
    score = 0
    b1, l1 = bipartitions_from_tree(t1, rooted=rooted)
    b2, l2 = bipartitions_from_tree(t2, rooted=rooted)
    maxScore = len(b1) + len(b2)
    for i in b1:
        found = False
        for j in b2:
            if set(min(i, key = lambda x: len(x))) == set(min(j, key = lambda x: len(x))):
                found = True
                break
        if not found:
            score += 1
    for i in b2:
        found = False
        for j in b1:
            if set(min(i, key = lambda x: len(x))) == set(min(j, key = lambda x: len(x))):
                found = True
                break
        if not found:
            score += 1
    return score, maxScore