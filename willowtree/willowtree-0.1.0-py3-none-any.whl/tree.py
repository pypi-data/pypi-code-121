from collections import deque
import os

class Node:
    def __init__(self, name='', edge_len = 0, parent = None):
        self.name = name
        self.length = edge_len
        self.parent = parent
        self.children = []

    def __str__(self):
        if self.name:
            return str(self.name)
        else:
            return ''
    
    def __len__(self):
        return len(list(self.get_leaves()))

    # Helper function for writing newick string
    def write_newick(self, terminate=True, format=0):
        if self.is_leaf():
            if format == 0 or format == 2:
                return self.name
            elif format == 1 or format == 3:
                return self.name + ':' + str(self.length)
        else:
            newick_str = '('
            for child in self.children:
                newick_str += child.write_newick(terminate=False, format=format) + ','
            newick_str = newick_str[:-1]
            newick_str += ')'
            if format == 2 or format == 3: #or terminate:
                newick_str += self.name
            if (format == 1 or format == 3) and not terminate:
                newick_str += ':' + str(self.length)
        if terminate:
            return newick_str + ';'
        else:
            return newick_str

    def set_name(self, name):
        self.name = name

    def set_len(self, edge_len):
        self.length = float(edge_len)

    def set_parent(self, parent):
        self.parent = parent

    # Sets an existing Node object as a child.
    def set_child(self, child):
        self.children.append(child)
        child.parent = self

    # Creates a new Node object as a child.
    def add_child(self, name='', edge_len = 0):
        child = Node(name = name, edge_len = float(edge_len), parent = self)
        self.children.append(child)
        return child

    def detach(self):
        self.parent.children.remove(self)
        self.parent = None
    
    # Given a subset of children, create a new clade and add it as a child.
    def resolve_polytomy(self, children, name=''):
        newNode = self.add_child(name=name)
        for node in children:
            node.detach()
            newNode.set_child(node)

    def is_leaf(self):
        return len(self.children) == 0
    
    def is_root(self):
        return self.parent is None

    def get_root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    #post order traversal (Left, Right, Root)
    def iter_postorder(self):
        visit_queue = deque()
        return_queue = deque()
        visit_queue.append(self)

        while visit_queue:
            node = visit_queue.pop()
            return_queue.append(node)
            if not node.is_leaf():
                visit_queue.extend(node.children)
        
        while return_queue:
            node = return_queue.pop()
            yield node

    #level order traversal, i.e. breadth first search from the root.
    def iter_descendants(self):
        nodes = deque()
        nodes.append(self)

        while nodes:
            node = nodes.popleft()
            nodes.extend(node.children)
            yield node

    def get_leaves(self):
        return [n for n in self.iter_postorder() if n.is_leaf()]

    def get_height(self):
        if self.is_leaf():
            return 0
        else:
            return max([1 + child.get_height() for child in self.children])

    def get_total_branchlen(self):
        return sum([node.length for node in self.iter_descendants()])


class Tree:
    def __init__(self, root=None, newick=None):
        self.root = root
        if newick:
            if os.path.exists(newick):
                f = open(newick)
                tree_str = f.readline()
                f.close()
                self.root = str_to_newick(tree_str)
            else:
                self.root = str_to_newick(newick)
    
    def __str__(self):
        return self.root.write_newick()

    def __iter__(self):
        return self.root.iter_descendants()

    def __len__(self):
        return len(list(self.iter_leaves()))

    #format codes --> 0: leaf names only, 1: leaf names + lengths only, 2: leaf and internal names, 3: leaf and internal names + lengths
    def print_newick(self, format=0):
        newick_str = self.root.write_newick(format=format)
        print(newick_str)

    def iter_postorder(self):
        return self.root.iter_postorder()
    
    def iter_descendants(self):
        return self.root.iter_descendants()
    
    def iter_leaves(self):
        for node in self.iter_descendants():
            if node.is_leaf():
                yield node
    
    def iter_path_to_leaf(self, leaf):
        path = []
        cur_node = leaf
        while not cur_node.is_root():
            path.append(cur_node)
            cur_node = cur_node.parent
        path.append(self.root)
        path.reverse()
        for node in path:
            yield node

    def has_leaf_names(self):
        for leaf in self.iter_leaves():
            if leaf.name == '':
                return False
        return True

    def set_leaf_names(self):
        count = 1
        for leaf in self.iter_leaves():
            if leaf.name == '':
                leaf.name = 'leaf' + str(count)
                count += 1
        self.cell_names = [node.name for node in self.iter_leaves()]

    # Sets both leaf and internal names.
    def set_node_names(self):
        internalcount = 1
        leafcount = 1
        for node in self.iter_descendants():
            if node.is_root():
                node.name = 'root'
            elif not node.is_leaf():
                node.name = 'internal' + str(internalcount)
                internalcount += 1
            elif node.is_leaf():
                node.name = 'leaf' + str(leafcount)
                leafcount += 1
        self.cell_names = [node.name for node in self.iter_leaves()]

    def get_tree_height(self):
        return self.root.get_height()
    
    def get_total_branchlen(self):
        return self.root.get_total_branchlen()

    # Get a Node object in the tree by name
    def ref_node(self, node_name):
        for node in self.iter_descendants():
            if node.name == node_name:
                return node

    def save(self, file_path, format=0):
        newick_str = self.root.write_newick(format=format)
        f = open(file_path, 'w+')
        f.write(newick_str)
        f.close()

    def find_LCA(self, leaves):
        queue = []
        queue.append(self.root)
        LCA_node = None
        while len(queue) > 0:
            cur_node = queue.pop(0)
            if set(leaves).issubset(set([leaf.name for leaf in cur_node.get_leaves()])):
                queue.extend(cur_node.children)
                LCA_node = cur_node
        return LCA_node

    def unroot(self):
        subtree = self.root.children[1]
        if subtree.is_leaf():
            subtree = self.root.children[0]
            if subtree.is_leaf():
                return None
        subtree.detach()
        node1, node2 = subtree.children[0], subtree.children[1]
        node1.detach()
        node2.detach()
        self.root.set_child(node1)
        self.root.set_child(node2)
        del subtree


def str_to_newick(newick_str):
    newick_str = newick_str.strip().replace(" ", "")
    split_str = newick_str[:-1].split(',')

    cur_node = None
    nodes = []

    for chunk in split_str:
        while chunk[0] == '(':
            new_node = Node()
            if cur_node:
                cur_node.set_child(new_node)
            cur_node = new_node
            chunk = chunk[1:]
        rest = chunk.split(')')
        if ':' in rest[0]:
            idx = rest[0].index(':')
            cur_node.add_child(name=rest[0][:idx], edge_len=rest[0][idx+1:])
        else:
            cur_node.add_child(name=rest[0])
        if len(rest) > 1:
            for part in rest[1:]:
                if ':' in part:
                    idx = part.index(':')
                    cur_node.set_name(part[:idx])
                    cur_node.set_len(part[idx+1:])
                else:
                    cur_node.set_name(part)
                    cur_node.set_len(0)
                if not cur_node.is_root():
                    cur_node = cur_node.parent
    return cur_node