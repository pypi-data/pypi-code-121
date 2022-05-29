import treelib
from treelib.tree import Tree
import os

print('\nMade with treelib v{}\n'.format(treelib.__version__))

class FileTree(Tree):

    
    def path_search(self, keywords, req_all_keywords=True, assert_on_disk=True, max_iter=1000):
        """
        gets the path from the unique ID (max tree length = 1000 to prevent unending search)
        """
        
        # handle string
        if type(keywords) is str:
            keywords = [keywords]

        # make sure keywords are unique
        keyword_set = set(keywords)
        keywords = list(keyword_set)
        
        satisfy_nodes = self.filter_nodes(lambda x: x.tag in keywords)
        
        paths = []
        for node in list(satisfy_nodes):

            keyword_path = []
            
            node_id = node.identifier
            node_tag = node.tag


            keyword_path = [node_tag]
            
            i = 0
            while (not node.is_root()) or (i>max_iter) :

                node = self.parent(node_id)
                node_id = node.identifier
                node_tag = node.tag
                                
                keyword_path = [node_tag] + keyword_path
                i += 1
                
            path = ''

            if req_all_keywords:
                if all([k in keyword_path for k in keyword_set]):
                    path = os.path.join(*tuple(keyword_path))
            else:
                path = os.path.join(*tuple(keyword_path))

            if path:
                if path not in paths:
                    paths += [path]
                    
        if assert_on_disk and len(paths)>0:
            for path in paths:
                if not os.path.isdir(path):
                    raise ValueError('Path not detected on disk')
        return paths
    

    def append_product_tree(self, root_node, *args):
        """
        takes in tag name of root and list of lists each of which
        will recursively add leaves
        """
        for i in args:
            assert(type(i) is list)

        def add_branch(parent_id, new_children):
            child_ids = []
            for child in new_children:
                child_ids += [self.create_node(child, parent=parent_id)]
            return child_ids

        root_id = root_node.identifier

        depth_counter = 0
        old_parent_ids = [root_id]

        while depth_counter<len(args):

            new_parent_ids = []
            new_children = args[depth_counter]

            for parent_id in old_parent_ids:
                child_ids = add_branch(parent_id, new_children)
                new_parent_ids += child_ids

            old_parent_ids = new_parent_ids.copy()
            depth_counter += 1
            
    def make_dirs(self,root=None, exist_ok=True):


        for ids in self.paths_to_leaves():
    

            tags = [str(self.get_node(id_val).tag) for id_val in ids]
            if root is not None:
                tags = [root] + tags
            dir_str = os.path.join(*tuple(tags))
                
            os.makedirs( dir_str, exist_ok=exist_ok )
            
        print('\nwritten directory tree -- (exist_ok={})'.format(exist_ok))
        


