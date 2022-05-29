'''
Author: SPeak Shen
Date: 2022-03-11 20:40:58
LastEditTime: 2022-03-12 14:30:15
LastEditors: SPeak Shen
Description: list
FilePath: /EasyUtils/src/eutils/EList.py
trying to hard.....
'''

class LNode:

    def __init__(self, data, pre=None, next=None):
        self.data = data
        self.pre = pre
        self.next = next

class EList:

    __mHeadNode = None
    __mIterNode = None

    def __init__(self):
    
        self.__mHeadNode = LNode(None)
        self.__mHeadNode.next = self.__mHeadNode
        self.__mHeadNode.pre = self.__mHeadNode

    def empty(self):
        
        return self.__mHeadNode.pre == self.__mHeadNode

    def add(self, node):
        self.push(node)

    def delete(self, node):

        if not isinstance(node, LNode):

            currNode = self.__mHeadNode.next

            while currNode != self.__mHeadNode and currNode.data != node:
                currNode = currNode.next

            if currNode != self.__mHeadNode:
                node = currNode
            else:
                return

        node.pre.next = node.next
        node.next.pre = node.pre

    def popBack(self):

        pass

    def push(self, node, trailer=True):

        if trailer:
            self.pushBack(node)
        else:
            self.pushFront(node)

    def pushFront(self, node):
        
        if not isinstance(node, LNode):
            node = LNode(node, self.__mHeadNode, self.__mHeadNode.next)
        else:
            node.next = self.__mHeadNode.next
            node.pre = self.__mHeadNode
        
        node.next.pre = node
        node.pre.next = node

    def pushBack(self, node):

        if not isinstance(node, LNode):
            node = LNode(node, self.__mHeadNode.pre, self.__mHeadNode)
        else:
            node.pre = self.__mHeadNode.pre
            node.next = self.__mHeadNode

        node.next.pre = node
        node.pre.next = node

    def __iter__(self):
        self.__mIterNode = self.__mHeadNode.next
        return self
 
    def __next__(self):

        if self.__mIterNode == self.__mHeadNode:
            raise StopIteration

        rNode = self.__mIterNode
        self.__mIterNode = rNode.next

        return rNode.data