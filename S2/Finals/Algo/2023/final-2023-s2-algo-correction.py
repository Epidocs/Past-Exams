# -*- coding: utf-8 -*-
"""
S2 - final 2
2019-05
"""

from algopy import bintre, avl
from avl_classics import rr, lr, lrr,rlr


class BinTreeSize:
    def __init__(self, key, left, right, size):
        self.key = key
        self.left = left
        self.right = right
        self.size = size


#------------------------------------------------------------------------------
#  exercise 1: copyWithSize

# __copySize(B) returns the pair (copy of B: BinTreeSize, its size: int)

def __copySize(B):
    if B == None:
        return(None, 0)
    else:
        (left, size1) = __copySize(B.left)
        (right, size2) = __copySize(B.right)
        size = 1 + size1 + size2
        return (BinTreeSize(B.key, left, right, size), size)
        
#or
        
def __copySize2(B):
    if B == None:
        return(None, 0)
    else:
        C = BinTreeSize(B.key, None, None, 1)
        (C.left, size1) = __copySize2(B.left)
        (C.right, size2) = __copySize2(B.right)
        C.size += size1 + size2
        return (C, C.size)
                
def copyWithSize(B):
    (C, size) = __copySize(B)
    return C

# v2: 
def __copyWithSize2(B):
    C = BinTreeSize(B.key, None, None, 1)
    if C.left != None:
        B.left = __copyWithSize2(B.left)
        C.size += C.left.size
    if B.right != None:
        C.right = __copyWithSize2(B.right)
        C.size += C.right.size
    return C  

def copyWithSize2(B):
    if B == None:   
        return None
    else:
        return __copySize2(B)
#------------------------------------------------------------------------------
#  exercise 2: insertion
    
def addBSTSize(x, A):
    if A == None:
        A = BinTreeSize(x, None, None, 1)
        return (A, True)
    else:
        if x < A.key:
            (A.left, insert) = addBSTSize(x, A.left)
        elif x > A.key:
            (A.right, insert) = addBSTSize(x, A.right)
        else:
            insert= False
        if insert:
            A.size += 1
        return (A, insert)
    
#------------------------------------------------------------------------------
#  exercise 3: median
    
def nthBST(B, k):
    if B.left == None:
        leftSize = 0
    else:
        leftSize = B.left.size
        
    if leftSize == k - 1:
        return B
    elif k <= leftSize:
        return nthBST(B.left, k)
    else:
        return nthBST(B.right, k - leftSize - 1)
        
def median(B):
    if B!= None:
        return nthBST(B, (B.size+1) // 2).key
    else:
        return None


############################ AVL #################################

# rebalancing after balance factor update: 
# A not empty, balance factor is in [-2, 2]
# if necessary,performs a rotation
# returns the tree and a boolean the indicates if the tree height has changed

def rebalancing(A):
    if abs(A.bal) < 2:
        return (A, False)
    if A.bal == 2:
        if A.left.bal == 1:
            return (rr(A), True)
        elif A.left.bal == 0:
            return (rr(A), False)
        else:
            return (lrr(A), True)
    else:   # A.bal == -2
        if A.right.bal == -1:
            return (lr(A), True)
        elif A.right.bal == 0:
            return (lr(A), False)
        else:
            return (rlr(A), True)

def rebalancing2(A):
    if abs(A.bal) < 2:
        return (A, False)
    if A.bal == 2:
        if A.left.bal == -1:
            A = lrr(A)
        else:
            A = rr(A)
    else:   # A.bal == -2
        if A.right.bal == 1:
            A = rlr(A)
        else:
            A = lr(A)
    return (A, A.bal == 0)