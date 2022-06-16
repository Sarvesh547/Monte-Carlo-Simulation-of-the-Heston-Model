#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import scipy.stats as st
import enum 


# In[2]:


# set i= imaginary number
i   = np.complex(0.0,1.0)

# This class defines puts and calls
class OptionType(enum.Enum):
    CALL = 1.0
    PUT = -1.0
    


# In[3]:


# Black-Scholes Call option price
def BS_Call_Option_Price(CP,S_0,K,sigma,tau,r):
    
    K = np.array(K).reshape([len(K),1])
    d1    = (np.log(S_0 / K) + (r + 0.5 * np.power(sigma,2.0)) 
    * tau) / float(sigma * np.sqrt(tau))
    d2    = d1 - sigma * np.sqrt(tau)
    if CP == OptionType.CALL:
        value = st.norm.cdf(d1) * S_0 - st.norm.cdf(d2) * K * np.exp(-r * tau)
    elif CP == OptionType.PUT:
        value = st.norm.cdf(-d2) * K * np.exp(-r * tau) - st.norm.cdf(-d1)*S_0
    return value


# In[4]:


def GeneratePathsGBMEuler(NoOfPaths,NoOfSteps,T,r,sigma,S_0):    
    Z = np.random.normal(0.0,1.0,[NoOfPaths,NoOfSteps])
    W = np.zeros([NoOfPaths, NoOfSteps+1])
   
    # Euler Approximation
    S1 = np.zeros([NoOfPaths, NoOfSteps+1])
    S1[:,0] =S_0
    
    time = np.zeros([NoOfSteps+1])
        
    dt = T / float(NoOfSteps)
    for i in range(0,NoOfSteps):
        # making sure that samples from normal have mean 0 and variance 1
        if NoOfPaths > 1:
            Z[:,i] = (Z[:,i] - np.mean(Z[:,i])) / np.std(Z[:,i])
        W[:,i+1] = W[:,i] + np.power(dt, 0.5)*Z[:,i]
        
        S1[:,i+1] = S1[:,i] + r * S1[:,i]* dt + sigma * S1[:,i] * (W[:,i+1] - W[:,i])
        time[i+1] = time[i] +dt
        
    # Retun S1 and S2
    paths = {"time":time,"S":S1}
    return paths


# In[5]:



def BS_Cash_Or_Nothing_Price(CP,S_0,K,sigma,tau,r):
    #Black-Scholes for cash or nothing option
    K = np.array(K).reshape([len(K),1])
    d1    = (np.log(S_0 / K) + (r + 0.5 * np.power(sigma,2.0)) 
    * tau) / float(sigma * np.sqrt(tau))
    d2    = d1 - sigma * np.sqrt(tau)
    if CP == OptionType.CALL:
        value = K * np.exp(-r * tau) * st.norm.cdf(d2)
    if CP == OptionType.PUT:
        value = K * np.exp(-r * tau) *(1.0 - st.norm.cdf(d2))
    return value


# In[6]:



def GeneratePathsGBMMilstein(NoOfPaths,NoOfSteps,T,r,sigma,S_0):    
    Z = np.random.normal(0.0,1.0,[NoOfPaths,NoOfSteps])
    W = np.zeros([NoOfPaths, NoOfSteps+1])
   
    # Milstein Approximation
    S1 = np.zeros([NoOfPaths, NoOfSteps+1])
    S1[:,0] =S_0
       
    time = np.zeros([NoOfSteps+1])
        
    dt = T / float(NoOfSteps)
    for i in range(0,NoOfSteps):
        # making sure that samples from normal have mean 0 and variance 1
        if NoOfPaths > 1:
            Z[:,i] = (Z[:,i] - np.mean(Z[:,i])) / np.std(Z[:,i])
        W[:,i+1] = W[:,i] + np.power(dt, 0.5)*Z[:,i]
        
        S1[:,i+1] = S1[:,i] + r * S1[:,i]* dt + sigma * S1[:,i] * (W[:,i+1] - W[:,i])                     + 0.5 * sigma **2.0 * S1[:,i] * (np.power((W[:,i+1] - W[:,i]),2) - dt)
        time[i+1] = time[i] +dt
        
    # Retun S1 and S2
    paths = {"time":time,"S":S1}
    return paths


# In[7]:



def EUOptionPriceFromMCPaths(CP,S,K,T,r):
    # S is a vector of Monte Carlo samples at T
    if CP == OptionType.CALL:
        return np.exp(-r*T)*np.mean(np.maximum(S-K,0.0))
    elif CP == OptionType.PUT:
        return np.exp(-r*T)*np.mean(np.maximum(K-S,0.0))

def CashofNothingPriceFromMCPaths(CP,S,K,T,r):
    # S is a vector of Monte Carlo samples at T
    if CP == OptionType.CALL:
        return np.exp(-r*T)*K*np.mean((S>K))
    elif CP == OptionType.PUT:
        return np.exp(-r*T)*K*np.mean((S<=K))


# In[8]:


def mainCalculation():
    CP= OptionType.CALL
    T = 1
    r = 0.06
    sigma = 0.3
    S_0 = 5
    K = [S_0]
    NoOfSteps =1000
    
    # Simulated paths
    NoOfPathsV = [100,1000,5000,10000]
    
    # Call price
    exactPrice = BS_Call_Option_Price(CP,S_0,K,sigma,T,r)[0]
    print("EUROPEAN OPTION PRICING")
    print("Exact option price = {0}".format(exactPrice))
    for NoOfPathsTemp in NoOfPathsV:
        np.random.seed(1) #we will iterate the paths[100,1000,5000,10000]
        PathsEuler    = GeneratePathsGBMEuler(NoOfPathsTemp,NoOfSteps,T,r,sigma,S_0)
        np.random.seed(1)
        PathsMilstein = GeneratePathsGBMMilstein(NoOfPathsTemp,NoOfSteps,T,r,sigma,S_0)
        S_Euler = PathsEuler["S"]
        S_Milstein = PathsMilstein["S"]
        priceEuler = EUOptionPriceFromMCPaths(CP,S_Euler[:,-1],K,T,r)
        priceMilstein = EUOptionPriceFromMCPaths(CP,S_Milstein[:,-1],K,T,r)
        print("For N = {0} Euler scheme yields option price = {1} and Milstein {2}"              .format(NoOfPathsTemp,priceEuler,priceMilstein))
        print("For N = {0} Euler error = {1} and Milstein  error {2}"              .format(NoOfPathsTemp,priceEuler-exactPrice,priceMilstein-exactPrice))
    
    # Cash or nothing price
    print("CASH OR NOTHING PRICING")
    exactPrice = BS_Cash_Or_Nothing_Price(CP,S_0,K,sigma,T,r)
    print("Exact option price = {0}".format(exactPrice))
    for NoOfPathsTemp in NoOfPathsV:
        np.random.seed(1)
        PathsEuler    = GeneratePathsGBMEuler(NoOfPathsTemp,NoOfSteps,T,r,sigma,S_0)
        np.random.seed(1)
        PathsMilstein = GeneratePathsGBMMilstein(NoOfPathsTemp,NoOfSteps,T,r,sigma,S_0)
        S_Euler = PathsEuler["S"]
        S_Milstein = PathsMilstein["S"]
        priceEuler = CashofNothingPriceFromMCPaths(CP,S_Euler[:,-1],K[0],T,r)
        priceMilstein = CashofNothingPriceFromMCPaths(CP,S_Milstein[:,-1],K[0],T,r)
        print("For N = {0} Euler scheme yields option price = {1} and Milstein {2}"              .format(NoOfPathsTemp,priceEuler,priceMilstein))
        print("For N = {0} Euler error = {1} and Milstein  error {2}"              .format(NoOfPathsTemp,priceEuler-exactPrice,priceMilstein-exactPrice))
mainCalculation()


# In[ ]:





# In[ ]:




