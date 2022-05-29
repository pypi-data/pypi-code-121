from functools import reduce
import random
def oneNeighbourCycle(self):
    neighbours, selfData = self.lookNeighbours()
    neighbour = neighbours[0]
    if selfData["val"] == self.target:
        if neighbour["val"] == 1:
            self.done = True
            return
        self.move(neighbour["id"])
        return
    if neighbour["val"] == self.target:
        self.move(neighbour["id"], 1)
        return
    if neighbour["val"] <= 0:
        self.move(neighbour["id"], neighbour["val"]-1)
        return
    self.move(neighbour["id"], neighbour["val"]+1)
    return

def twoNeighboursCycle(self):
    neighbours, selfData = self.lookNeighbours()
    if selfData["val"] == self.target:
        neighbours = list(filter(lambda x: x["val"] != self.target, neighbours))
        if reduce((lambda x, y : x["occupied"] and y["occupied"]), neighbours) or reduce((lambda x, y : x["val"] == 1 and y["val"] == 1), neighbours):
            self.done = True
            return
        for i in neighbours:
            if not i["occupied"] and i["val"] != 1:
                self.move(i["id"])
                return
        return       
    elif reduce((lambda x, y : x["val"] == self.target or y["val"] == self.target), neighbours):
        otherNode = list(filter(lambda x: x["val"] != self.target, neighbours))[0]
        targetNode = list(filter(lambda x: x["val"] == self.target, neighbours))[0]
        if otherNode["val"] == 2 or otherNode["val"] == 1:
            self.move(targetNode["id"], 1)
            return
        
        self.move(otherNode["id"], 1)
        return

    if reduce((lambda x, y : x["val"] <= 0 and y["val"] <= 0), neighbours):
        if reduce((lambda x, y : x["val"] == y["val"]), neighbours):
            if reduce((lambda x, y : x["occupied"] and y["occupied"]), neighbours) or reduce((lambda x, y : not x["occupied"] and not y["occupied"]), neighbours):
                randomIndex=random.randint(0,len(neighbours)-1)
                self.move(neighbours[randomIndex]["id"], neighbours[randomIndex]["val"] - 1)
                return
            
            
            node = list(filter(lambda x: not x["occupied"], neighbours))[0]
            self.move(node["id"], node["val"] - 1)
            return 
        
        node, otherNode = reduce((lambda x, y : (x, y) if abs(x["val"]) < abs(y["val"]) else (y, x)), neighbours)
        self.move(node["id"], node["val"] - 1)
        return 
    
    elif reduce((lambda x, y : x["val"] > 0 and y["val"] > 0), neighbours):
        node, otherNode = reduce((lambda x, y : (x, y) if x["val"] < y["val"] else (y, x)), neighbours)
        self.updateWhiteboardValue(node["val"] + 1)
        if otherNode["val"] - node["val"] > 2:
            if not otherNode["occupied"]:
                self.move(otherNode["id"])
                return
            self.move(node["id"])
            return
        
        self.move(node["id"])
        return
    node, otherNode = reduce((lambda x, y : (x, y) if x["val"] > y["val"] else (y, x)), neighbours)
    self.updateWhiteboardValue(node["val"] + 1)
    if otherNode["occupied"]:
        self.move(node["id"])
        return
    self.move(otherNode["id"])
    return            

def moreThanTwoNeighboursCycle(self):
    #to do: save length of zeronodes, lessthannodes and morethannodes is some variable and use it instead of len() function.
    neighbours, selfData = self.lookNeighbours()
    greaterThanNodes = sorted(list(filter((lambda x: x["val"] > 0), neighbours)), key=lambda x: x["val"])
    lessThanNodes = sorted(list(filter((lambda x: x["val"] < 0), neighbours)), key=lambda x: x["val"])
    zeroNodes = list(filter((lambda x: x["val"] == 0), neighbours))
    targetNodes = list(filter((lambda x: x["val"] == self.target), neighbours))
    lenGreaterThanNodes = len(greaterThanNodes)
    lenLessThanNodes = len(lessThanNodes)
    lenZeroNodes = len(zeroNodes)
    if selfData["val"] == self.target:
        neighbours = list(filter(lambda x: x["val"] != self.target, neighbours))
        if reduce((lambda x, y: x and y), map(lambda x: x["val"] == 1, neighbours)) or reduce((lambda x, y: x and y), map(lambda x: x["occupied"], neighbours)):
            self.done = True
            return
        other = list(filter(lambda x: x["val"] != 1, neighbours))[0]
        self.move(other["id"])
        return
    
    if len(targetNodes) > 0:
        self.updateWhiteboardValue(1)
        if len(list(filter(lambda x: x["val"] == 1 or x["val"] == 2, neighbours))) == len(neighbours) - 1:
            self.move(targetNodes[0]["id"])
            return
        if lenZeroNodes > 0:
            randomIndex=random.randint(0,lenZeroNodes-1)
            self.move(zeroNodes[randomIndex]["id"])
            return
        
        if lenLessThanNodes > 0:
            self.move(lessThanNodes[0]["id"])
            return
        
        
        other = list(filter(lambda x: x["val"] != 2, neighbours))
        randomIndex=random.randint(0,len(other)-1)
        self.move(other[randomIndex]["id"])
        return
    
    if lenZeroNodes == 0 and lenGreaterThanNodes == 0:
        self.move(lessThanNodes[-1]["id"], lessThanNodes[-1]["val"] - 1)
        return
    
    if lenLessThanNodes == 0 and lenZeroNodes == 0:
        self.updateWhiteboardValue(greaterThanNodes[0]["val"] + 1)
        
        for i in range(lenGreaterThanNodes - 1, -1, -1):
            if greaterThanNodes[i]["val"] - greaterThanNodes[0]["val"] > 2:
                if not greaterThanNodes[i]["occupied"]:
                    self.move(greaterThanNodes[i]["id"])
                    return
        
        self.move(greaterThanNodes[0]["id"])
        return
    
    if lenLessThanNodes == 0 and lenGreaterThanNodes == 0:
        randomIndex=random.randint(0,lenZeroNodes-1)
        self.move(zeroNodes[randomIndex]["id"], -1)
        return
    
    if lenGreaterThanNodes == 0:
        randomIndex=random.randint(0,lenZeroNodes-1)
        self.move(zeroNodes[randomIndex]["id"], lessThanNodes[-1]["val"] - 1)
        return
    
    if lenZeroNodes == 0:
        self.move(lessThanNodes[0]["id"], greaterThanNodes[0]["val"] + 1)
        return

    randomIndex=random.randint(0,lenZeroNodes-1)
    self.move(zeroNodes[randomIndex]["id"], greaterThanNodes[0]["val"] + 1)
    return 