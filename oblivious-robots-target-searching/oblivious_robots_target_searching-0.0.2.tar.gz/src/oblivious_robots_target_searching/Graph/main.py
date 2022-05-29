from ..Robot import Robot
import networkx
import random
from matplotlib import pyplot as plt
from .chordAdder import multi_chord

def ranks(sample):
    #Return the ranks of each element in an integer sample.
    indices = sorted(range(len(sample)), key=lambda i: sample[i])
    return sorted(indices, key=lambda i: indices[i])

def sample_with_minimum_distance(n, k, d):
    #Sample of k elements from range(n), with a minimum distance d.
    sample = random.sample(range(n-(k-1)*(d-1)), k)
    return [s + (d-1)*r for s, r in zip(sample, ranks(sample))]

class Playground:
    def __init__(self, sim=True):
        self.robots = {}
        self.target = None
        self.targetVal = None
        self.graph = None
        self.pos = None
        self.sim = sim
        self.whiteboardValues = {} 
        self.noOfRobots=None
        self.noOfNodes=None
        
    def setupRobots(self,args):
        randoms=random.sample(range(self.graph.number_of_nodes()),args['noOfRobots'])        
        for i in randoms:
            robot = Robot(i,self.targetVal,self.sim)
            self.robots[robot.id] = robot
            
    def setupRingWithChordsGraph(self, args):
        noOfNodesInChord=2*args['val']//(args['val']//args['noOfChords'])
        initNoOfNodes=args['val']-noOfNodesInChord
        self.graph = networkx.cycle_graph(initNoOfNodes)
        if not self.sim:
            self.pos = networkx.circular_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}            
        multi_chord(self,args['noOfChords'],noOfNodesInChord)
        return
    
    def setupBinomialTree(self, args):
        self.graph = networkx.binomial_tree(args["r"])
        if not self.sim:
            self.pos = networkx.kamada_kawai_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupCompleteGraph(self, args):
        self.graph = networkx.complete_graph(args['r'])
        if not self.sim:
            self.pos = networkx.circular_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupCompleteMultipartiteGraph(self, args):        
        self.graph = networkx.complete_multipartite_graph(args['r'],args['h'])
        if not self.sim:
            self.pos = networkx.multipartite_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupCircularLadderGraph(self, args):
        self.graph = networkx.circular_ladder_graph(args['r'])
        if not self.sim:
            self.pos = networkx.kamada_kawai_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupCirculantGraph(self, args):
        offset=[]
        for _ in range(args['r']):
            offset.append(random.randint(0,args['h']))
        self.graph=networkx.circulant_graph(args['r'],offset)
        if not self.sim:
            self.pos=networkx.spring_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return

    def setupChordalCycleGraph(self, args):
        self.graph=networkx.chordal_cycle_graph(args['r'])
        if not self.sim:
            self.pos=networkx.fruchterman_reingold_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupDorogovtsevGoltsevMendesGraph(self, args):
        self.graph=networkx.dorogovtsev_goltsev_mendes_graph(args['r'])
        if not self.sim:
            self.pos=networkx.planar_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupFullRaryTree(self, args):
        self.graph=networkx.full_rary_tree(args['r'],args['h'])
        if not self.sim:
            self.pos=networkx.kamada_kawai_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupLadderGraph(self, args):
        self.graph=networkx.ladder_graph(args['r'])
        if not self.sim:
            self.pos=networkx.kamada_kawai_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupDuplicationDivergenceGraph(self, args):
        self.graph=networkx.duplication_divergence_graph(args['r'],1)
        if not self.sim:
            self.pos=networkx.kamada_kawai_layout(self.graph)
        self.whiteboardValues = {}
        self.robots = {}
        return
    
    def setupWhiteboard(self):
        for node in self.graph.nodes():
            if node == self.target:
                self.whiteboardValues[node] = self.targetVal
            else:
                self.whiteboardValues[node] = 0
    
    def inputGraph(self):
        pass
    
    def setupInterative(self):
        print('Select type of graph:')
        graphs = {
            1: {
                "type": "binomial_tree",
                "name": "Binomial Tree"
            },
            2: {
                "type": "complete_graph",
                "name": "Complete Graph"
            },
            3: {
                "type": "complete_multipartite_graph",
                "name": "Complete Multipartite Graph"
            },
            4: {
                "type": "circular_ladder_graph",
                "name": "Circular Ladder Graph"
            },
            5: {
                "type": "circulant_graph",
                "name": "Circulant Graph"
            },
            6:{
                "type": "chordal_cycle_graph",
                "name": "Chordal Cycle Graph"
            },
            7: {
                "type": "dorogovtsev_goltsev_mendes_graph",
                "name": "Dorogovtsev Goltsev Mendes Graph"
            },
            8: {
                "type": "full_rary_tree",
                "name": "Full r-ary Tree"
            },
            9: {
                "type": "ladder_graph",
                "name": "Ladder Graph"
            },
            10: {
                "type": "duplication_divergence_graph",
                "name": "Duplication Divergence Graph"
            },
            11: {
                "type": "ring-with-chords",
                "name": "Ring with Chords Graph"
            }            
        }
        for key, value in graphs.items():
            print(f"{key}. {value['name']}")
            
        typeOfGraph = int(input("Enter your choice:"))
        if typeOfGraph not in graphs.keys():
            print("Invalid choice")
            return
        typeOfGraph = graphs[typeOfGraph]["type"]            
        
        if typeOfGraph == 'ring-with-chords':
            val = int(input("Enter number of nodes (5-1000): "))
            args = {
                "type": "ring-with-chords",
                "val": val,
                "noOfRobots": int(input(f"Enter number of robots (1-{val}): ")),
                "noOfChords": int(input(f"No of chords (0-{val//4}): "))
            }
            self.setupRingWithChordsGraph(args)
        elif typeOfGraph == 'binomial_tree':
            r = int(input("Enter height of the tree (2-10): "))
            args = {
                "type": "binomial_tree",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{2**r}): "))
            }
            self.setupBinomialTree(args)
        elif typeOfGraph == 'complete_graph':
            r = int(input("Enter number of nodes in the graph (3-100): "))
            args = {
                "type": "complete_graph",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{r}): "))
            }
            self.setupCompleteGraph(args)
        elif typeOfGraph == 'complete_multipartite_graph':
            r = int(input("Enter number of nodes in 1st partition (1-100): "))
            h= int(input("Enter number of node in 2nd partition (1-100): "))
            args = {
                "type": "complete_multipartite_graph",
                "r": r,
                "h": h,
                "noOfRobots": int(input(f"Enter number of robots (1-{r+h}): "))
            }
            self.setupCompleteMultipartiteGraph(args)
        elif typeOfGraph == 'circular_ladder_graph':
            r = int(input("Enter number of nodes in the circles (2-250): "))
            args = {
                "type": "circular_ladder_graph",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{r*2}): "))
            }
            self.setupCircularLadderGraph(args)
        elif typeOfGraph == 'circulant_graph':
            r = int(input("Enter number of nodes in the graph (5-250): "))
            args = {
                "type": "circulant_graph",
                "r": r,
                "h": int(input(f"Enter the maximum degree of offset of a node (1-{r}): ")),
                "noOfRobots": int(input(f"Enter number of robots (1-{r}): "))
            }
            self.setupCirculantGraph(args)
        elif typeOfGraph == 'chordal_cycle_graph':
            r = int(input("Enter number of nodes in the graph (4-250): "))
            args = {
                "type": "chordal_cycle_graph",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{r}): "))
            }
            self.setupChordalCycleGraph(args)
        elif typeOfGraph == 'dorogovtsev_goltsev_mendes_graph':
            r = int(input("Enter number of nodes in the graph (3-6): "))
            args = {
                "type": "chordal_cycle_graph",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{5*r-1}): "))
            }
            self.setupDorogovtsevGoltsevMendesGraph(args)
        elif typeOfGraph == 'full_rary_tree':
            h = int(input("Enter number of nodes in the graph (5-625): "))
            args = {
                "type": "full_rary_tree",
                "r": int(input("Enter number of children (2-5): ")),
                "h": h,
                "noOfRobots": int(input(f"Enter number of robots (1-{h}): "))
            }
            self.setupFullRaryTree(args)
        elif typeOfGraph == 'ladder_graph':
            r = int(input("Enter number of steps in the ladder (2-100): "))
            args = {
                "type": "ladder_graph",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{2*r}): "))
            }
            self.setupLadderGraph(args)
        elif typeOfGraph == 'duplication_divergence_graph':
            r = int(input("Enter number of nodes in the graph (8-150): "))
            args = {
                "type": "duplication_divergence_graph",
                "r": r,
                "noOfRobots": int(input(f"Enter number of robots (1-{r}): "))
            }
            self.setupDuplicationDivergenceGraph(args)
        else:    
            pass
        self.target=random.randint(0,self.graph.number_of_nodes()-1)
        self.targetVal=random.randint(2*self.graph.number_of_nodes(), 3*self.graph.number_of_nodes())
        self.noOfNodes=self.graph.number_of_nodes()
        self.noOfRobots=args['noOfRobots']
        self.setupRobots(args)
        self.setupWhiteboard()
    
    def setupSimulation(self, args):
        typeOfGraph = args['type']
        if typeOfGraph == 'ring-with-chords':
            self.setupRingWithChordsGraph(args)
        elif typeOfGraph == 'binomial_tree':
            self.setupBinomialTree(args)
        elif typeOfGraph == 'complete_graph':
            self.setupCompleteGraph(args)
        elif typeOfGraph == 'complete_multipartite_graph':
            self.setupCompleteMultipartiteGraph(args)
        elif typeOfGraph == 'circular_ladder_graph':
            self.setupCircularLadderGraph(args)
        elif typeOfGraph == 'circulant_graph':
            self.setupCirculantGraph(args)
        elif typeOfGraph == 'chordal_cycle_graph':
            self.setupChordalCycleGraph(args)
        elif typeOfGraph == 'dorogovtsev_goltsev_mendes_graph':
            self.setupDorogovtsevGoltsevMendesGraph(args)
        elif typeOfGraph == 'full_rary_tree':
            self.setupFullRaryTree(args)
        elif typeOfGraph == 'ladder_graph':
            self.setupLadderGraph(args)
        elif typeOfGraph == 'duplication_divergence_graph':
            self.setupDuplicationDivergenceGraph(args)
        else:
            pass
        self.target=random.randint(0,self.graph.number_of_nodes()-1)
        self.targetVal=random.randint(2*self.graph.number_of_nodes(), 3*self.graph.number_of_nodes())
        self.noOfNodes=self.graph.number_of_nodes()
        self.noOfRobots=args['noOfRobots']
        self.setupRobots(args)
        self.setupWhiteboard()
        
    def setup(self, args={}):
        if self.sim:
            self.setupSimulation(args)
            return
        self.setupInterative()
        return
        
    def checkTargets(self):
        ans = True
        for i in self.robots.values():
            ans = ans and i.done
        return not ans
        
    def cycleRobots(self):
        for _, val in self.robots.items():
            val.cycle(self)
        
    def run(self):
        run = True
        visualSwitch = False
        counter = 0
        while run:
            self.cycleRobots()
            run = self.checkTargets()
            counter += 1
            if self.sim: continue
            print("----------------------- Cycle {} -----------------------".format(counter))
            plt.clf()
            color_map = []
            edge_colors = []
            robots_pos = list(map(lambda x: x.pos, self.robots.values()))
            for node in self.graph:
                if node in robots_pos:
                    if self.whiteboardValues[node] > 0:
                        color_map.append('purple')
                    else:
                        color_map.append('red')
                elif node == self.target:
                    color_map.append('blue')
                else: 
                    color_map.append('green')
            for node in self.graph:
                if node == self.target:
                    edge_colors.append('blue')  
                else: 
                    edge_colors.append('black')
            labels = {}
            if visualSwitch:
                for key, value in self.whiteboardValues.items():
                    labels[key] = f'{key}'
            else:
                for key, value in self.whiteboardValues.items():
                    labels[key] = f'{value}'
            #if counter % 20 == 0:
            #    visualSwitch = not visualSwitch
            try:
                plt.title(f'Total nodes -> {self.noOfNodes} : No. of robots -> {self.noOfRobots} : Target at {self.target}\nRobots at target -> {len(list(filter(lambda x: x.pos==self.target, self.robots.values())))} :No. of cycles -> {counter}')     
                networkx.draw_networkx_nodes(self.graph, self.pos, node_size=330, node_color=color_map, edgecolors=edge_colors)
                networkx.draw_networkx_labels(self.graph, self.pos,labels,font_size=9, font_color='white')
                networkx.draw_networkx_edges(self.graph, self.pos)
                plt.pause(0.0001)
            except Exception as e:
                print(str(e))
            #input()#remove for val>=20
        if not self.sim:
            plt.show()
        if self.sim:
            return [self.noOfNodes,self.noOfRobots, counter-2]
        else:
            print(self.noOfNodes, self.noOfRobots, counter)
        
            
    # SetupGraph SetupWhiteBoard Run to control the flow
    
# if __name__ == '__main__':
#     P = Playground(True)