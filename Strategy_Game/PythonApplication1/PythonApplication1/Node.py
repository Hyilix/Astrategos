#This library is dedicated to handle the Tree of Nodes in the gameplay. The Kernel
#and Nodes (structures) will form a Tree to know what Node is connected to the Kernel
#and what is not. What is connected to the Kernel emits a radius in which the player
#can construct structures and units into it. Units or structures not "connected"
#to the Kernel via Nodes will act normal.

import math

TreeRoot = None     #The root of the tree. When in gameplay, TreeRoot will become the player's Kernel.

NodeList = []   #This array stores all the nodes of a player from the map.
NodesFound = []

class TreeNode():
    def __init__(self, Position, Range):
        self.Position = Position    #World position of the Node (structure). This is a tupple (x,y), and this is the center of the Structure.
        self.Parent = None    #Pointer to another TreeNode
        self.Children = []    #Array of TreeNodes
        self.Range = Range  #The range of the Node.
        self.Powered = False    #If it's connected to the Kernel (directly or indirectly), Powered is True

        NodeList.append(self)   #Add the node to the array.

    def InitTree(self):     #Start from the root, find Nodes, and from these Nodes search until no Node is left out.
        global NodesFound
        NodesFound = [TreeRoot]

        for node in NodeList:
            if node != self and node not in NodesFound: #!!!!NOTE: this search will not do it completely. Must redo.
                if self.CheckCollision(node) == True:
                    NodesFound.append(node)
                    self.Add(node)
                    self.Powered = True

    def Search_Powered_Node(self):
        NodesSearched = []

        for node in NodeList:
            if node != self and node not in NodesSearched and node.Powered == True:
                if self.CheckCollision(node) == True:
                    print(None)

    def Unpower_Children(self):     #Weird name, but it iterates trough every children (and grandchildren) and unpowers it
        self.Powered = False
        for child in self.Children:
            child.Unpower_Children()

    def Remove(self):
        NodeList.remove(self)   #Removes the node from the array and the Tree
        self.Parent.Children.remove(self)   
        self.Parent = None
        self.Unpower_Children()

    def Add(self, target):  #Add the Node to the Tree relatively to the target Node. This function shouldn't be called on the Kernel Node.
        #Special Case for connection with Kernel Node:
        if self.Parent == None and NodeList.index(target) == 0:
            self.Parent = target
        elif NodeList.index(target) == 0:
            return  #You don't want to make the Kernel Node a child of another Node. You just don't.

        if target.Parent == None:
            target.Parent = self
        else:
            target.Children.append(self)
            self.Parent = target
            self.Powered = True

    def CheckCollision(self, target):   #Checks if the target Node and this Node are intersecting. This can be very bad for a lot of Nodes because of n^2 complexity
        return math.sqrt((self.Position[0] - target.Position[0]) ** 2 + (self.Position[1] - target.Position[1]) ** 2) <= min(self.Range, target.Range)

    