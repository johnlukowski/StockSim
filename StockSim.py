import numpy as np
import matplotlib.pyplot as plt

# Minimum nterval at which trades take place in seconds (86400 is a day)
INTERVAL = 300
# Number of companies in the simulation
COMPANIES = 500


# Calculate the interest rate on a margin account
def getMarginInterest(balance):
    if balance<50000: return .0475
    if balance<100000: return .04
    if balance<250000: return .0325
    if balance<500000: return .02375
    if balance<1000000: return .0175
    return .015

# Get the new margin account balance after applying interest
def addMarginInterest(balance, days):   return balance*getMarginInterest(balance)*days/365

class Order(list):
    def __init__(self, agent, amount, price):
        self._container = [agent, amount, price]
    def __iter__(self):
        return (o for o in self._container)
    def __repr__(self):
        return self._container
    def __getitem__(self, item):
        if isinstance(item, (int,slice)):
            return self._container[item]
        return [self._container[i] for i in item]
    def __setitem__(self, item, value):
        if isinstance(item, int):
            self._container[item] = value
        else:
            for i in item:
                self._container[i] = value
    def __delitem__(self, item):
        if isinstance(item, (int,slice)):
            del self._container[item]

class Company:
    classId = 0

    def __init__(self, history):
        self.id = Company.classId
        Company.classId+=1
        self.value = history[-1] if history[-1]>1000 else 1000                          # Dont start a company worth less than $1000
        self.totalShares = max(round((max(history) - min(history))/5000*.65)*500, 500)  # Starting number of shares based on ~$10 per and value of company. only trade 65%. Minimum 500
        self.currentShares = self.totalShares                                           # Current number of tradeable shares left
        self.sellOrders = []                                                            # Container to hold agents trying to sell this stock in the format (agent, amount, price), oldest first
        self.buyOrders = []                                                             # Container to hold agents trying to buy this stock in the format (agent, amount, price), oldest last
        self.asking = round(self.value/self.totalShares*100)/100                        # Initial asking price of the stock
        self.history = []                                                               # History was just for creation, reset it for company to be reborn in stock market

    def __repr__(self):
        return self.id

    # Create a new company with simulated value history using geometric brownian motion
    def newCompany(mu, sigma, seed, age):   return Company(seed*(1+np.random.normal(loc=mu, scale=sigma, size=age)).cumprod())

    # The difference between highest and lowest points of a company's value
    def swing(self):    return max(self.history) - min(self.history)

    # get the current asking prices on the market for this stock (low to high)
    def prices(self):   return sorted([i[-1] for i in self.sellOrders]) if len(self.sellOrders) else [self.asking]

    # Iterate one cycle of the market for this company
    def iterate(self):
        history += [self.asking]
        for buyOrder in self.buyOrders[::-1]:       # Iterate through the buy orders and fulfill them if possible. Iterates backwards (starting at oldest orders)
            if len(self.sellOrders):                # If there are any sell orders, try to buy from them
                buyable = [order for order in self.sellOrders if order[-1]<=offer]
                for sellOrder in buyable:           # Iterating through the sell orders under the buy order's offer price
                    price = sellOrder[2]
                    if sellOrder[1]<=buyOrder[1]:   # Not enough shares in the current sell order, will move to the next after fulfilling from here
                        amount = sellOrder[1]
                        sellOrder[0].wallet += amount*price
                        buyOrder[0].wallet -= amount*price
                        if self in buyOrder[0].portfolio:   buyOrder[0].portfolio[self] += amount
                        else:   buyOrder[0].portfolio.update({self:amount})
                        buyOrder[1]-=amount
                        self.sellOrders.remove(sellOrder)
                    else:                           # Enough shares in the current sell order, fulfill the full buy order
                        amount=buyOrder[1]
                        sellOrder[0].wallet += amount*price
                        buyOrder[0].wallet -= amount*price
                        if self in buyOrder[0].portfolio:   buyOrder[0].portfolio[self] += amount
                        else:   buyOrder[0].portfolio.update({self:amount})
                        sellOrder[1]-=amount
                        buyOrder[1]=0
                    self.asking = price #Current company asking price is always the last share sold price    
                    if buyOrder[1]==0:  break
            if buyOrder[1] and self.currentShares and buyOrder[2] >= self.asking:   # If the company has shares left below the buy order's offer price, fulfill from the company
                price = buyOrder[2]
                if self.currentShares <= buyOrder[1]:   # Not enough shares held by the company, fullfill what is possible
                    amount = self.currentShares
                    self.currentShares -= amount
                    buyOrder[0].wallet -= amount*price
                    self.value += amount*price
                    buyOrder[1] -= amount
                else:                                   # Enough shares held by the compeny, fulfill the full buy order
                    amount = buyOrder[1]
                    self.currentShares -= amount
                    buyOrder[0].wallet -= amount*price
                    self.value += amount*price
                    buyOrder[1] = 0
                self.asking = price
            if not buyOrder[1]: self.buyOrders.remove(buyOrder) # If this buy order was fulfilled, clear if from the buy orders
                            
                    

class Agent:
    def __init__(self, seed, strategy):
        self.portfolio = {}
        self.wallet = seed

# Put together a list of companies to start out with
companies = [Company.newCompany(.0015+np.random.randint(5)/10000, .02+np.random.randint(20)/1000, 4000+np.random.randint(2000), 1000+np.random.randint(1000)) for i in range(COMPANIES)]


# shorting. Broker sells the stock and opens a margin account with interest. 30% minumum balance
# if you short 300 shares of a $10 stock, you have taken a #3000 loan. Must maintain $900 in the account. the balance is based on market balue of the shares, if it went to $9, balance would be 2700, if $11, 3300.

print(companies[0].asking)
