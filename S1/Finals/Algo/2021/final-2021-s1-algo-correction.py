
# -*- coding: utf-8 -*-
"""
Dec. 2016
@author: nathalie
"""


def test(x, L):
    i = len(L) - 1
    while i >= 0 and L[i] != x:
        i = i - 1
    return i >= 0
    
#------------------------------------------------------------------------------
# ex 4 q1 : 2 points

def int_to_list(n, p):
    L = []
    while n != 0:
        L.append(n % 10)
        n = n // 10
    for i in range(p-len(L)):
        L.append(0)
    return L

def int_to_list2(n, p):
    L = []
    while p > 0:
        L.append(n % 10)
        n = n // 10
        p -= 1
    return L
      

#------------------------------------------------------------------------------
# ex 4 q2 : 3 points

def list_to_ints(L):
    left = 0
    right = 0
    n = len(L)
    for i in range(n):
        left = left * 10 + L[i]
        right = right * 10 + L[n-i-1]
    return (left, right)

def list_to_ints2(L):
    left = 0
    right = 0
    p = 1
    for i in range(len(L)):
        left = left * 10 + L[i]
        right = right + L[i]*p
        p = p * 10
    return (left, right)


    
#------------------------------------------------------------------------------
# ex 5 q1 : 1.5 points
    
def hist(L):
    '''
    L contains only digits (from 0 to 9)
    hist(L) builds an histogram of values in L
    '''
    H = []
    for i in range(10):
        H.append(0)
    # ou H = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for e in L:
        H[e] += 1
    return H

#------------------------------------------------------------------------------
# ex 5 q2 : 2.5 points

def sort(L):
    H = hist(L)
    L = []
    for i in range(10):
        for nb in range(H[i]):
            L.append(i)
    return L
    
#------------------------------------------------------------------------------
# ex 6 : 5 points

    
def Kaprekar(n, p):
    L = []
    while not test(n, L):
        print(n, end=' -> ')
        L.append(n)
        digits = int_to_list(n,p)
        digits = sort(digits)
        (low, high) = list_to_ints(digits)
        n = high - low
    print(n)
    



'''
main
'''

def nb_digits(n):
    p = 0
    while n != 0:
        p = p + 1
        n = n // 10
    return p

def main():
    n = -1
    while n <= 0:
        n = int(input("Give a non-zero positive integer\n"))
    Kaprekar(n, nb_digits(n))

#main()

