#This library is dedicated to handle the Tree of Nodes in the gameplay. The Kernel
#and Nodes (structures) will form a Tree to know what Node is connected to the Kernel
#and what is not. What is connected to the Kernel emits a radius in which the player
#can construct structures and units into it. Units or structures not "connected"
#to the Kernel via Nodes will act normal.
import pygame
import math

TreeRoot = None     #The root of the tree. When in gameplay, TreeRoot will become the player's Kernel.

NodeList = []   #This array stores all the nodes of a player from the map.
NodesFound = []

CircleColor = (204,204,0)

def InitTree():     #Start from the root, find Nodes, and from these Nodes search until no Node is left out.
    global NodesFound
    NodesFound = [TreeRoot]

    for node in NodesFound:
        for target in NodeList:
            if target != node and target not in NodesFound:
                if node.CheckCollision(target) == True:
                    NodesFound.append(target)
                    target.Add(node)
                    target.Powered = True

def Find_connections():
    for node in NodesFound:
        for target in NodeList:
            if target != node and target not in NodesFound:
                if node.CheckCollision(target) == True:
                    NodesFound.append(target)
                    target.Add(node)
                    target.Powered = True

def Draw_tree_circles(node, screen, size, offset):  #Go trough the tree and draw all circles
    node.DrawCircle(screen, size, offset)
    for child in node.Children:
        Draw_tree_circles(child, screen, size, offset)

def getNodeFromObj(obj):
    for node in NodeList:
        if node.obj == obj.Position:
            return node

    return None

class Node():
    def __init__(self, Position, Range, obj):
        self.Position = Position    #Matrics position of the Node (structure). This is a tupple (x,y), and this is the center of the Structure.
        self.Parent = None    #Pointer to another TreeNode
        self.Children = []    #Array of TreeNodes
        self.Range = Range  #The range of the Node.
        self.Powered = False    #If it's connected to the Kernel (directly or indirectly), Powered is True
        self.obj = obj.Position  #The object associated with the Node

        NodeList.append(self.obj)   #Add the node to the array.

    def Search_Powered_Node(self):  #Searched for any powered node on the map.
        for node in NodeList:
            if node != self and node.Powered == True:
                if self.CheckCollision(node) == True:
                    self.Add(node)
                    break

    def Unpower_Children(self):     #Weird name, but it iterates trough every children (and grandchildren) and unpowers it
        self.Powered = False
        for child in self.Children:
            child.Unpower_Children()

    def Remove(self):   #Removes the node from the array and the Tree
        NodesFound.remove(self.obj)
        self.Parent.Children.remove(self)   
        self.Parent = None
        self.Unpower_Children()

    def Kill(self):     #Removes the node from the game
        NodesFound.remove(self.obj)
        self.Remove()
        self.obj = None
        del self

    def Add(self, target):  #Add the Node to the Tree relatively to the target Node. This function shouldn't be called on the Kernel Node.
        #Special Case for connection with Kernel Node:
        if self.Parent == None and NodeList.index(target) == 0:
            self.Parent = target
            target.Children.append(self)
            self.Powered = True
            NodesFound.append(self.obj)
        elif NodeList.index(target) == 0:
            return  #You don't want to make the Kernel Node a child of another Node. You just don't.

        else:
            if target.Parent == None:
                target.Parent = self
                self.Children.append(target)
            else:
                target.Children.append(self)
                self.Parent = target
                self.Powered = True
                NodesFound.append(self.obj)

    def CheckCollision(self, target):   #Checks if the target Node and this Node are intersecting. This can be very bad for a lot of Nodes because of n^2 complexity
        return math.sqrt((self.Position[0] - target.Position[0]) ** 2 + (self.Position[1] - target.Position[1]) ** 2) <= max(self.Range, target.Range)

    def CheckBuildingInRadius(self, target):
        return math.sqrt((self.Position[0] - target.position[0] - 0.5) ** 2 + (self.Position[1] - target.position[1] - 0.5) ** 2) <= self.Range

    def DrawCircle(self, screen, size, offset):
        pygame.draw.circle(screen, CircleColor, (self.Position[0] * size - offset[0], self.Position[1] * size - offset[1]), self.Range * size, 1)