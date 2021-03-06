# -*- coding: utf-8 -*-
"""
Programming Exercise - Part 2.

File name: part2.py
Author: Gabriel Farias Caccaos
E-mail: gabriel.caccaos@gmail.com
Date created: 02/12/2018
Python version: 3.6.7
"""

def norm(vector):
    """Calculates the 1-norm of a vector.
    
    Args:
        vector (list): The list which represents the vector.
        
    Returns:
        int: Sum of the absolute values of the vector.
    """
    
    return sum(abs(element) for element in vector)

def deltaList(list1, list2):
    """Calculates the element-wise subtraction of two lists.
    
    Args:
        list1 (list): The frist list.
        list2 (list): The second list.
        
    Returns:
        list: Element-wise subtraction of the two lists.
    """
    
    return [a - b for a, b in zip(list1, list2)]

def sumList(list1, list2):
    """Calculates the element-wise sum of two lists.
    
    Args:
        list1 (list): The frist list.
        list2 (list): The second list.
        
    Returns:
        list: Element-wise sum of the two lists.
    """
    
    return [a + b for a, b in zip(list1, list2)]

def multiplyList(vector, scalar):
    """Calculates the element-wise product of a vector by a scalar.
    
    Args:
        vector (list): The list which represents the vector.
        scalar (float): The value of the scalar.
        
    Returns:
        list: Element-wise product of the vector by the scalar.
    """
    
    return [scalar*element for element in vector]

def scoresRank(scores):
    """Return the list of pages in decreasing order of score."""
	
    return sorted(range(len(scores)), key = scores.__getitem__, reverse = True)

def compressedSparseRow(matrix):
    """Performs the CSR compression (in "row-major" order) to a matrix.
    
    Args:
        matrix (list): a list of lists.
    Returns:
        values (list): values of the non-zero entries in the matrix
        rows (list): rows of the non-zero entries in the matrix
        columns (list): columns of the non-zero entries in the matrix
    """
    
    nRows = len(matrix)
    nCols = len(matrix[0])
    
    # Data structure for the non-zero entries
    values, rows, columns = [], [], []
    
    # Row-wise loop through the matrix
    for row in range(nRows):
        for column in range(nCols):
            value = matrix[row][column]
            if value != 0:
                values.append(value)
                rows.append(row)
                columns.append(column)
    
    return values, rows, columns

def getNumPages(numGroups):
    """Returns the number of pages of a network with chief-tribe architecture.
	"""
	
    numChiefs = numGroups
    numIndians = sum(page for page in range(1, numGroups + 1))
    
    return numChiefs + numIndians

def createAdjacencyMatrix(numGroups):
    """Returns the adjacency matrix of a network with chief-tribe architecture.
	"""
	
    numPages = getNumPages(numGroups)
    chiefsList = []

    # Create adjency matrix (full of zeros)
    adjacencyMatrix = [[0 for column in range(numPages)] for row in range(numPages)]

    # Handle links to pages (including chiefs) that belong to the same group
    for group in range(numGroups):
        chiefPage = int(group*(group + 3)/2)
        chiefsList.append(chiefPage)

        groupPages = list(range(chiefPage, chiefPage + group + 2))

        for thisPage in groupPages:
            targetPages = [page for page in groupPages if page != thisPage]
            for targetPage in targetPages:
                adjacencyMatrix[thisPage][targetPage] = 1
    
    # Handle links between chief pages
    for chiefPage in chiefsList:
        targetPages = [page for page in chiefsList if page != chiefPage]
        for targetPage in targetPages:
            adjacencyMatrix[chiefPage][targetPage] = 1
    
    return adjacencyMatrix

def createLinkMatrix(numGroups):
    """Returns the link matrix of a network given its adjacency matrix.
	
	To do this, the columns of the adjacency matrix must be normalized (this
	fixes the weights of the links that comes to the same page).
    """
	
    numPages = getNumPages(numGroups)
    
    adjacencyMatrix = createAdjacencyMatrix(numGroups)
    linkMatrix = [row for row in adjacencyMatrix]
    
    for page in range(numPages):
        numIncomingLinks = sum(pointedBy[page] for pointedBy in adjacencyMatrix)
        for otherPage in linkMatrix:
            otherPage[page] /= numIncomingLinks
        
    return linkMatrix

def getScores(linkMatrix):
    """Calculates the vector of scores of a network described by the link
	matrix.
    
    Args:
        linkMatrix (list): The list (of lists) which represents the link matrix.

    Returns:
        list: The (final) importance scores of the pages.
    """
    
    epsilon = 1E-5
    m = 15E-2
    
    # Apply sparse row compression on the link matrix:
    # get the non-zero entries values and positions
    values, rows, columns = compressedSparseRow(linkMatrix)
    
    numPages = len(linkMatrix)
    initialScores = [1./numPages]*numPages

    # First iteration
    oldScores = initialScores
    y = [0]*numPages
    for (link, page, otherPage) in zip(values, rows, columns):
        y[page] += link*oldScores[otherPage]
    y = multiplyList(y, 1./norm(y))
    
    normInitialScores = multiplyList(initialScores, m)
    normNewScores = multiplyList(y, 1 - m)
    newScores = sumList(normNewScores, normInitialScores)

    deltaScores = deltaList(newScores, oldScores)
    
    # Following iterations
    while norm(deltaScores) >= epsilon:
        oldScores = newScores
        for (link, page, otherPage) in zip(values, rows, columns):
            y[page] += link*oldScores[otherPage]
        y = multiplyList(y, 1./norm(y))
 
        normInitialScores = multiplyList(initialScores, m)
        normNewScores = multiplyList(y, 1 - m)
        newScores = sumList(normNewScores, normInitialScores)

        deltaScores = deltaList(newScores, oldScores)
   
    return newScores

def pageRank(linkMatrix):
    """Performs the ranking of the pages and prints the ranking-score table for
	a network described by the link matrix.
    """
    
    numPages = len(linkMatrix)
    numGroups = int(((8*numPages + 9)**0.5 - 3)/2)
    
    chiefsList = [int(group*(group + 3)/2) for group in range(numGroups)]
    
    scores = getScores(linkMatrix)
    rankingList = scoresRank(scores)
    
    printedGroups = []
    print('Rank\tPage(s)\t\tGroup\tImportance score')
    
    rank = 0
    for page in rankingList:
        # Find chief and group of this page
        chief = [chiefPage for chiefPage in chiefsList if chiefPage <= page][-1]
        group = int(((8*chief + 9)**0.5 - 3)/2)
        
        # Handle chief pages
        if page in chiefsList:
            score = scores[page]
            print('{0: >2}\t{1: >3}\t\t{2: >2}\t{3:.5f}'.format(rank + 1, page + 1, group + 1, score))
            rank += 1
        
        # Handle indian pages
        elif group not in printedGroups:
            score = scores[page]
            lastGroupPage = chief + group + 1
            if lastGroupPage != page:
                print('{0: >2}\t{1: >3} to {2: >3}\t{3: >2}\t{4:.5f}'.format(rank + 1,page + 1, lastGroupPage + 1, group + 1, score))
            else:
                print('{0: >2}\t{1: >3}\t\t{2: >2}\t{3:.5f}'.format(rank + 1, page + 1, group + 1, score))
            printedGroups.append(group)
            rank += 1

# Main program
if __name__ == "__main__":
    numGroups = 20					# this value can be changed (default = 20)

    linkMatrix = createLinkMatrix(numGroups)
    pageRank(linkMatrix)