import math

TreeRoot = None     #The root of the tree. When in gameplay, TreeRoot will become the player's Kernel.

NodeList = []   #This array stores all the nodes of a player from the map.
NodesFound = []

class TreeNode():
    def __init__(self, Position, Parent, Children, Range):
        self.Position = Position    #World position of the Node (structure). This is a tupple (x,y), and this is the center of the Structure.
        self.Parent = Parent    #Pointer to another TreeNode
        self.Children = Children    #Array of TreeNodes
        self.Range = Range  #The range of the Node.

        NodeList.append(self)   #Add the node to the array.

    def Remove(self):
        NodeList.remove(self)   #Removes the node from the array.

    def CheckCollision(self, target):   #Checks if the target Node and this Node are intersecting.
        return math.sqrt((self.Position[0] - target.Position[0]) ** 2 + (self.Position[1] - target.Position[1]) ** 2) <= min(self.Range, target.Range)

    def InitTree(self):     #Start from the root, find Nodes, and from these Nodes search until no Node is left out.
        global NodesFound
        NodesFound = [TreeRoot]

        for node in NodesFound:
            print(node)