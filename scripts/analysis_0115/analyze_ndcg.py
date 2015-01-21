"""
analyze the behaviour of NDCG

Q: what's the difference between measuring gain, e.g., 
NDCG and measuring effort?
"""
import pylab
import numpy as np
from math import log

"""
- Assume we have a ranked list of length N, containing
R relevant documents. 
- Assume the last document (nth) is relevant, and we use it to switch
with previously ranked non-relevant document. 
- We can observe when the switch happens at rank x, how NDCG changes, 
document changes, and how effort to find R documents changes.
"""
def switch_case():
    # Let NDCG_o be the original NDCG score of the ranked list.
    # If the switch point is at rank x, then we have the new NDCG
    # DCG_n/iNDCG = (DCG_o + 1/log_2(x+1)- 1/log_2(N+1))/iNDCG
    # where iNDCG is a constant
    
    # Let N = 100, x = 1:100, plot the trend
    N = 100
    X = range(1, N+1)
    diff_ndcg = [1/log(x+1, 2) - 1/log(N+1, 2) for x in X]
    pylab.figure()
    pylab.plot(X, diff_ndcg) 
    

    # N is the original effort to find R relevant documents.
    # K is the rank of R-1th relevant document.
    # x is the switch point. 
    # We have diff_effort = x if x > K, and K if x<K. x and K should not be equal, 
    # as we assume x has a non-relevant document, which is switched to a relevant
    # document. 
    pylab.figure()
    for K in [10, 20, 50]:
        diff_effort = [N-K if x<K else N-x for x in X]
        pylab.plot(X, diff_effort)


    # What if we measure P@K. 
    # if x < K, the swtich from a non-relevant doc to a relevant doc results in 
    # diff = 1/K
    pylab.figure()
    for K in [10., 20., 50.]:
        diff_pK = [0 if x>K else 1/K for x in X]
        pylab.plot(X, diff_pK)


if __name__ == '__main__':
    switch_case()
    pylab.show()


