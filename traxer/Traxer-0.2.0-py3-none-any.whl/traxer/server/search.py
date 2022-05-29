
def search_exp(prop : str):
    """Search all experiments that satisfy 'prop'
    prop format:
    - && : and
    - || : or
    
    Args:
        prop (str): A proposition to be evaluated
    Return:
        exps (Array<Experiments>): List of experiments that satisfy prop
    """
    exps = []

    return exps

class PropTree:

    def __init__(self, prop : str):
        self.left, self.right = self.construct(prop)
    
    def construct(self, prop):
        # Detect blocks
        level = 0
        block_position = -1
        for i in range(len(prop)):
            if prop[i] == "(":
                level += 1
                if level == 1:
                    # Begin block
                    ...
            else: 
                if level == 0:
                    # Begin block
                    ...

            if prop[i] == ")":
                if level > 0:
                    level -= 1
                else: 
                    raise ValueError("There is too much closing parenthesis")