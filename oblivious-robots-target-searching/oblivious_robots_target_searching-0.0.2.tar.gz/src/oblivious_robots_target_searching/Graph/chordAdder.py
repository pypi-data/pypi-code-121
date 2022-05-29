import random

def randomListWithFixedSum(m, n):
    arr = [0] * m
    
    for i in range(n) :
        arr[random.randint(0, n) % m] += 1
    return arr


def ranks(sample):
    #Return the ranks of each element in an integer sample.
    indices = sorted(range(len(sample)), key=lambda i: sample[i])
    return sorted(indices, key=lambda i: indices[i])

def sample_with_minimum_distance(n, k, d):
    #Sample of k elements from range(n), with a minimum distance d.
    sample = random.sample(range(n-(k-1)*(d-1)), k)
    return [s + (d-1)*r for s, r in zip(sample, ranks(sample))]

# def multi_chord(P, noOfChords, noOfNodes,):
#     #only add chords between nodes on the circle
#     chordPos = sample_with_minimum_distance(P.graph.number_of_nodes(), 2*noOfChords, P.graph.number_of_nodes()//(2*noOfChords))
#     ChordNodes= randomListWithFixedSum(noOfChords,noOfNodes)
#     for i in range(noOfChords):
#         add_chord(P, ChordNodes[i], chordPos[2*i], chordPos[2*i+1])
        
def multi_chord(P, noOfChords, noOfNodes):
    ChordNodes= randomListWithFixedSum(noOfChords,noOfNodes)
    for i in range(noOfChords):
        chordPos = sample_with_minimum_distance(P.graph.number_of_nodes(), 2, P.graph.number_of_nodes()//(2*noOfChords))
        add_chord(P, ChordNodes[i], chordPos[0], chordPos[1])
        
def add_chord(P, noOfNodes, strPos, endPos):
    
    if noOfNodes == 0:
        P.graph.add_edge(strPos, endPos)
        return
    n=P.graph.number_of_nodes()
    for i in range(noOfNodes):
        P.graph.add_node(n+i)
        if not P.sim:
            x = P.pos[strPos][0] + ((P.pos[endPos][0] - P.pos[strPos][0])/(noOfNodes+1)*(i+1))
            y = P.pos[strPos][1] + ((P.pos[endPos][1] - P.pos[strPos][1])/(noOfNodes+1)*(i+1))
            P.pos[n+i] = [x,y]
        if i:
            P.graph.add_edge(n+i-1, n+i)
    P.graph.add_edge(strPos, n)
    P.graph.add_edge(n+noOfNodes-1,endPos)

