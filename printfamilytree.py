# Object to store blocks of text for printing a tree of basePerson's descendents
#
# Recursion may continue indefinitely if the tree contains cycles, but I don't
# think it's possible to have cycles unless people are added to someone's 
# groups directly, without the use of the Tree() structure
class TextBlock:
    
    def __init__(self, tree, basePerson):
        
        if basePerson not in tree.people:
            raise Exception('{} not found in tree.'.format(basePerson.name))
            
        self.tree = tree
        self.basePerson = basePerson
        self.parents = basePerson.partners
        self.spaceNeeded = None
        self.stems = {}
        
        #Different formats for couples
        if self.parents.size() == 2:
            self.parentText = '{} --- {}'.format(self.basePerson.name, self.basePerson.getPartner().name)

        elif self.parents.size() == 1:
            self.parentText = '{}'.format(self.basePerson.name)
            
        else:
            raise Exception("{}'s parent group has incorrect size".format(self.basePerson))


        self.childTextBlocks = []
        self.children = self.basePerson.children

        for child in self.children:
            
            childTextBlock = TextBlock(tree, child)
            self.childTextBlocks.append(childTextBlock)

        
    # Returns a minimum width needed for the block to ensure the blocks 
    # involving basePerson's children have sufficient space
    def spaceBelowNeeded(self):

        #Only calculate space if it has not been claculated before
        if self.spaceNeeded is None:
            
            #Space needed for keep basePerson's children's blocks
            childSpace = sum([child.spaceBelowNeeded() for child in self.childTextBlocks])
            #Space necessary to fit basePerson and their partner
            parentSpace = self.parents.size() * max([len(parent.name) for parent in self.parents]) + 2 + 5*(self.parents.size() == 2)
            
            
            self.spaceNeeded = max(childSpace, parentSpace)
                
        return self.spaceNeeded

    # Returns a string for the current levels partners, with any necessary padding for entries below.
    # String returned has length spaceNeededBelow()
    def partnerStem(self):
        lineLength = self.spaceBelowNeeded()
        
        #2 parents case
        if self.parents.size() == 2:
            center = int((self.spaceBelowNeeded() + 1) / 2)                     #Center of line
            maxLen = max([len(parent.name) for parent in self.parents])         #Max name length
            
            offsetLeft = center - 3 - len(self.basePerson.name)                 #Space in line at left before names
            offsetRight = center - 3 - len(self.basePerson.getPartner().name)   #Space in line at right after names
            
            stem = ' ' *  offsetLeft + self.parentText + ' ' * offsetRight
            return stem
        
        else:
            nameLength = len(self.basePerson.name)                  
            offsetLeft = int((lineLength - nameLength) / 2)                     #Space in line at left before names
            offsetRight = lineLength - offsetLeft - nameLength                  #Space in line at right after names
              
            stem = ' ' * offsetLeft + self.parentText+ ' '*offsetRight
            return stem
             
             
    # returns a string containing the stem below the partnerStem (vertical line towards children)
    def lowerStem(self):
        
        if self.children.size() != 0:
            center = int((self.spaceBelowNeeded() + 1) / 2)                     #Center of line
            offsetLeft = center-1                                               #Space in line at left before line
            offsetRight = self.spaceBelowNeeded() - center                      #Space in line at right after line
            return ' ' * offsetLeft + '|' + ' ' * offsetRight
        
        else:
            return ' ' * self.spaceBelowNeeded()
         
    # returns a string containing the stem above the partnerStem (vertical line towards parents)
    def upperStem(self):
        
        center = int((self.spaceBelowNeeded() + 1) / 2)                         #Center of line
        
        #1 parent case
        if self.parents.size() == 1:                                            
            offsetLeft = center-1                                               #Space in line at left before name
            offsetRight = self.spaceBelowNeeded() - center                      #Space in line at right after name
            return ' ' * offsetLeft + '|' + ' ' * offsetRight
        
        #2 parent case
        else: 
            nameCenter = center - 3 - int(len(self.basePerson.name)/2)          #Center of basePerson's name
            offsetLeft = nameCenter - 1                                         #Space in line at left before name
            offsetRight = (self.spaceBelowNeeded() - nameCenter)                #Space in line at right after name
            return ' ' * offsetLeft + '|' + ' ' * offsetRight
    
    def __str__(self):
        return '{}: {}'.format(self.basePerson.name, str(self.children))
    

    # Returns a tuple of strings which, when printed in sequence, show the family tree below basePerson
    # Each element of the tuple is a horizontal line of the family tree.
    def createBlock(self):
        
        # Necessary when one branch of the tree contains more generations than others
        # Returns a tuple of: tuples with equal length, padded with whitespace if length was not maximal 
        # NOTE: (final line of a block is whitespace)
        def addMissingDepth(tuples):
            if len(tuples) == 0:
                return tuples
                
            maxDepth = max(len(t) for t in tuples)                                 # Total depth of the tree
            
            return (tuple(t[i] if i in range(0, len(t)) else t[len(t) - 1] for i in range(0,maxDepth)) for t in tuples)
        
        # Necessary when a child's block takes less space than the parent's block
        # Returns a tuple of: strings with padded width
        #
        # NOTE: COULD BE OPTIMISED FOR SPACE BY OFFSETTING THE CENTER
        def addMissingWidth(tuples, parentWidth):
            if len(tuples) == 0:
                return tuples
            
            missingWidth = max(parentWidth - len(tuples[0]), 0)                     # Width needed to add

            leftPad = int((missingWidth + 1)/ 2)
            rightPad = missingWidth - leftPad
            
            return tuple(' ' * leftPad + row + ' ' * rightPad for row in tuples)
        
        # Creates tuple of blocks for children of basePerson
        childList = tuple(child.createBlock() for child in self.childTextBlocks)
        childList2 = addMissingDepth(childList)

        # This generator gives tuples of strings from each child that should be concatenated into 1 string
        gen = zip(*childList2)
        
        # Tuple of concatenated strings, each string representing a line in the printed tree.
        childCon0 = tuple(''.join(textTuple) for textTuple in gen)
        
        childConcatText = addMissingWidth(childCon0, self.spaceBelowNeeded())
        
        
        firstInd = None
        lastInd = None
        
        # Creates "horizontalStem", a horizontal line string to connect siblings to their parents
        if len(childConcatText) != 0:
            for index in range(0, len(childConcatText[0])):
                
                letter = childConcatText[0][index]
                if letter == '|':
                    if firstInd == None:
                        firstInd = index+1
                    lastInd = index 
                    
                
            vertLineBool = (self.basePerson.children.size() == 1)                   # Whether basePerson has exactly 1 child
                
            offsetLeft = (firstInd - vertLineBool)                                  # Space in line at left before line
            lineLength = lastInd - firstInd                                         # Length of horizontal line
            offsetRight = self.spaceBelowNeeded() - lastInd - vertLineBool          # Space in line at left before line
            
            horizontalStem = ' ' * offsetLeft + '-' * lineLength + '|' * vertLineBool + ' ' * offsetRight
            
        else:
            horizontalStem = ' ' * self.spaceBelowNeeded()
            
        
        parentConcatText = (self.upperStem(), self.partnerStem(), self.lowerStem())
        
        return (*parentConcatText, horizontalStem, *childConcatText)
    
    def printBlock(self):
        text = []
        block = self.createBlock()
        
        for index in range(0, len(block) - 2):          # The -2 is to remove 2 lines of whitespace below the tree
            text.append(block[index])
            
            if index is not len(block)-3:               # Do not append new line character on final line
                text.append('\n')
            
        return ''.join(text)



