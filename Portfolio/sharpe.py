#!/usr/bin/python3

import numpy as np

def TangentPortfolio(rskret,covar,rskfr):
    A = (1/covar)*(rskret-rskfr)
    A /= sum(A)
    pret=rskret.T*A
    prsk=np.power(A.T*(covar*A),0.5)
    return A.T,pret,prsk


mu=np.matrix([[0.13],[0.11],[0.19]])
cov=np.matrix([[0.04, 0.004, 0.02],[0.004, 0.09, 0.09],[0.02,0.09,0.16]])
rf=0.05
 
w,ret,rsk=TangentPortfolio(mu,cov,rf)
print("risk:")
print(w)
print("Expected Portfolio Return and Risk")
print(ret,rsk)
sharpe=(ret-rf)/rsk
print("sharpe ratio:")
print(sharpe)
