import printfamilytree as pft

#Set of all relations
relationSet = set(['partners','children','parents','siblings'])

#Output: the relation of person B to person A, when given the relationship of person A to person B.
inverseRelMap = {'parents': 'children', 'siblings': 'siblings', 'partners': 'partners', 'children': 'parents' }

# Adds relationship between person1 and person2, and combines appropriate groups.
# "relation" is the relationship of person2 to person1.
# This function works on the principle that adding any new relation combines 2 parent groups and 2 sibling groups
#
#
# NOTE: SHOULD NOT BE USED DIRECTLY, USED BY Tree.addViaRelation
def addRelation(person1, person2, relation):
    
    # Sets the correct "parents" and "siblings" groups
    if relation == 'siblings':
        partners1 = getattr(person1, 'parents')
        partners2 = getattr(person2, 'parents')
        siblings1 = person1.siblings
        siblings2 = person2.siblings
        
    elif relation == 'partners':
        partners1 = person1.partners
        partners2 = person2.partners
        siblings1 = getattr(person1, 'children')
        siblings2 = getattr(person2, 'children')
        
    elif relation == 'parents':
        partners1 = person1.partners
        partners2 = getattr(person2, 'parents')
        siblings1 = getattr(person1, 'children')
        siblings2 = person2.siblings
        
    elif relation == 'children':
        partners1 = getattr(person1, 'parents')
        partners2 = person2.partners
        siblings1 = person1.siblings
        siblings2 = getattr(person2, 'children')
    
    else:
        raise Exception("Invalid relation '{}', relation must be one of {}".format(relation, relationSet))
    
    #Adds each parent from partners2 to partners1, and reassigns their partners and children.
    for partner in partners2:
        if partners1.addPerson(partner) == 1:
            partner.setGroup('partners', partners1)
            partner.setGroup('children', siblings1)
          
    #Adds each child from siblings2 to siblings1, and reassigns their parents and siblings
    for sibling in siblings2:
        if siblings1.addPerson(sibling) == 1:
            sibling.setGroup('parents', partners1)
            sibling.setGroup('siblings', siblings1)

    
class Person:
    
    def __init__(self, name):
        self.name = name
        self.parents = Group(2)
        self.siblings = Group()
        self.partners = Group(2)
        self.children = Group()
        
        self.siblings.addPerson(self)
        self.partners.addPerson(self)      
        
        
    # NOTE: DO NOT USE DIRECTLY, USED BY addRelation.
    #       USING DIRECTLY CAUSES DISPARITY BETWEEN PERSON'S GROUP AND TREE
    #       PUT HERE FOR MORE CLARITY IN USAGE, SHOULD CHANGE LATER
    def setGroup(self, groupName, group):
        if groupName in relationSet:
            setattr(self, groupName, group)
        else:
            raise Exception("Invalid relation '{}', relation must be one of {}".format(relation, relationSet))
    
    def getPartner(self):
        p1 = [partner for partner in self.partners if partner is not self]
        if len(p1) == 1:
            return p1[0]
        
        return None
    
    def hasPartner(self):
        return len(self.partners) == 2
            
    def __str__(self):
        return self.name
    
    def prettyPrint(self):
        name = self.name
        
        line11 = '{}: '.format(name)
        line12 = 'Parents:  {}\n'.format(self.parents.listStr(self))
        
        # whitespace to place group names in columns.
        whitespace = ' '*(len(name) + 2)
        
        line3 = whitespace + 'Siblings: {}\n'.format(self.siblings.listStr(self))
        line4 = whitespace + 'Partner:  {}\n'.format(self.partners.listStr(self))
        line5 = whitespace + 'Children: {}\n'.format(self.children.listStr(self))
        
        return (line11 + line12) + line3 + line4 + line5


class Group:
    
    def __init__(self, maximum=-1):
        # maximum: max number of people allowed in group, -1 if no max
        self.people = []
        self.maximum = maximum
        
    def __iter__(self):
        return self.people.__iter__()
        
    def size(self):
        return len(self.people)
        
    def getFirst(self):
        #returns first person in group
        if self.size() == 0:
            return None
        return self.people[0]
        
    def hasMax(self):
        #returns whether the group has a maximum size
        return not self.maximum == -1
    
    # Adds person to group (if maximum is not exceeded, and person is not already in group)
    # Returns 1 if person was added sucessfully, and 0 if person was already in group
    # Raises exception is maximum would be exceeded
    def addPerson(self, person):
        
        if person not in self.people:
            
            if self.size() == self.maximum:
                raise Exception("Could not add '{}' to group {}: Maximum people in group exceeded".format(person.name, self))
                
            self.people.append(person)
            return 1
            
        else:
            return 0
            
    #returns list of names in group, excluding person
    def listStr(self, person):
        return [obj.name for obj in self.people if obj != person]
    
    def __str__(self):
        return str([person.name for person in self.people])
        
class Tree: 
    
    def __init__(self):
        #Set of all people in tree
        self.people = set()
        #Maps a person to their respective connected component
        self.personToComponent = {}
        #List of all connected components
        self.components = []
        
    #Removes component from list of components
    def removeComponent(self, comp):
        self.components.remove(comp)
        
    #Returns number of people in tree
    def size(self):
        return len(self.people)
    
    #Returns the number of connected components of the tree
    def numComponents(self):
        return len(self.components)
    
    #Checks if tree is connected (and non-empty)
    def isConnected(self):
        return self.numComponents == 1
    
    #Adds a person to the tree
    def addPerson(self, person):
        if person in self.people:
            return 
            
        #Adds person to set of people in tree
        self.people.add(person)
        #Adds new component containing new person
        newComp = Group()
        newComp.addPerson(person)
        self.components.append(newComp)
        self.personToComponent[person] = newComp
        
        
    # Adds two people to the tree via a relationship 
    # 'relation' describes person1's relation to person2
    def addViaRelation(self, person1, person2, relation):
        success1 = self.addPerson(person1)
        success2 = self.addPerson(person2)
        
        p1Comp = self.personToComponent[person1]
        p2Comp = self.personToComponent[person2]
        
        if p1Comp == p2Comp:
            if person1 in getattr(person2, relation):
                return
            raise Exception('{} and {} are already related via a different relation'.format(person1.name, person2.name))
            
        addRelation(person1, person2, relation)
        
        for person in p2Comp:
            p1Comp.addPerson(person)
            self.personToComponent[person] = p1Comp
                
        self.removeComponent(p2Comp)
            
    # adjacentRelationMap = {'children': ['children','partners'],\
    #           'parents' : ['parents', 'siblings'],\
    #           'siblings': ['partners', 'children'],
    #           'partners' : ['children', 'siblings', 'parents'],\
    #           None : ['siblings', 'partners', 'parents', 'children']}

    # Adds information from tree2 into self.
    def combineWith(self, tree2):
        pass

    # Returns direct relation of person1 to person2
    # Raises exception if either person is not in the tree    
    def getRelation(self, relative1, relative2):
        
        peopleSet = set([relative1, relative2])
        masterQueue = [[(relative1, relative2, "")]]
        
        relationList = ['partners','parents','children','siblings']
        
        for index, person in zip([1,2],[relative1, relative2]):
            if person not in self.people:
                raise Exception('relative{} was not found in tree.'.format(index))
                
        queueNum = 0
        foundPath = None
        for queue in masterQueue:
            if masterQueue == None:
                break   
            
            queueNum += 1
            
            for person1, person2, path in queue:
                if masterQueue == None:
                    break

                for groupName in relationList:
                                        
                    if person1 in getattr(person2, groupName):
                        foundPath = path + ' ' + groupName
                        masterQueue = None
                        break

                    for newPerson in getattr(person2, groupName):
                        if newPerson in peopleSet:
                            continue
                        
                        # print('({} {} includes {})'.format(relative2, groupName + ' ' + path, newPerson))
                
                        if queueNum >= len(masterQueue):
                            masterQueue.append([])
                            
                        peopleSet.add(newPerson)
                        masterQueue[queueNum].append((person1, newPerson, path + ' ' + groupName))
                        

                        
        if foundPath != None:
            return foundPath[1:]
        
        return 'No Relation'
            
    def __str__(self):
        return 'People: {} \n Size: {}\n Components: {}\n Num Comps: {}'\
            .format([obj.name for obj in self.people], self.size(), [[person.name for person in comp] for comp in self.components] ,self.numComponents())
            
    def prettyPrint(self, basePerson):
        block = pft.TextBlock(self, basePerson)
        return block.printBlock()
            
    
    