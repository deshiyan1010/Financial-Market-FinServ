import yfinance as yf

import pandas as pd

import riskfolio.Portfolio as pf
import riskfolio.PlotFunctions as plf
import riskfolio.RiskFunctions as rk

import numpy as np

import matplotlib.pyplot as plt

from pprint import pprint

class PortfolioOptmizer:

    def __init__(self):
        pass


    def getFromFile(self,filename):
        df = pd.read_csv(filename,index_col='Date')

        for col in df.columns[1:]:
            df = df.astype({col:'int32'})
        
        return df
    


    def _weightsOptimizer(self,df,obj='Sharpe',annualized_min_return=None,annualized_max_volatility=None):
        df = df.pct_change().dropna()


        if annualized_min_return!=None and annualized_max_volatility==None:
            port = pf(returns=df,lowerret=annualized_min_return/252)

        elif annualized_max_volatility!=None and annualized_min_return==None:
            port = pf(returns=df,upperdev=annualized_max_volatility/252**0.5)

        port.assets_stats(method_mu='hist', method_cov='hist', d=0.94)

        model='Classic'
        rm = 'MV' 
        hist = True 
        rf = 0
        l = 0

        t_factor=252

        w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)


        risk = rk.Sharpe_Risk(w,port.cov,port.returns,rm=rm,rf=rf,alpha=0.05)*t_factor**0.5

        return {x:y for x,y in zip(df.columns,np.array(w.T)[0])},port,risk



    def piePlot(self,w,title = 'Sharpe Mean Variance',others=0.02,nrow=25,cmap='tab20',height=6,width=10,ax=None):
        weights_df = pd.DataFrame.from_dict({x:[y] for x,y in w.items()},orient='index',columns=['weights'])
        ax = plf.plot_pie(w=weights_df, title=title, others=others, nrow=nrow, cmap = cmap, height=height, width=width, ax=ax)
        plt.show()

    def frontierPlot(self,port,w):
        w = pd.DataFrame.from_dict({x:[y] for x,y in w.items()},orient='index',columns=['weights'])
        model='Classic'
        rm = 'MV' 
        hist = True 
        rf = 0
        
        points = 50
        frontier = port.efficient_frontier(model=model, rm=rm, points=points, rf=rf, hist=hist)

        label = 'Max Risk Adjusted Return Portfolio' # Title of plot
        mu = port.mu
        cov = port.cov
        returns = port.returns
        ax = plf.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm, rf=rf, alpha=0.05, cmap='viridis', w=w, label=label, marker='*', s=16, c='r', height=6, width=10, ax=None)
        plt.show()

    def getWeights(self,tickList=None,filename=None,lookBack='6mo',obj='Sharpe',annualized_min_return=None,annualized_max_volatility=None):
        
        if lookBack not in ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']:
            raise Exception("lookBack must be one of the following\n'1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max'")

        if filename==None and tickList!=None:
            df = pd.DataFrame()
            for ticker in tickList:
                tick = yf.Ticker(ticker)
                hist = tick.history(period=lookBack)
                df[ticker] = hist['Close']

        elif filename!=None and tickList==None:
            df = self.getFromFile(filename)

        else:
            raise Exception("Either filename or tickList must be provided.")
        

        if annualized_min_return!=None and annualized_max_volatility==None:
            weights,port,risk = self._weightsOptimizer(df,obj=obj,annualized_min_return=annualized_min_return)

        elif annualized_max_volatility!=None and annualized_min_return==None:
            weights,port,risk = self._weightsOptimizer(df,obj=obj,annualized_max_volatility=annualized_max_volatility)

        else:
            raise Exception("Either annualized_min_return or annualized_max_volatility must be provided...")

        self.frontierPlot(port,weights)
        # self.piePlot(weights)

        return weights,risk


if __name__=="__main__":
    po = PortfolioOptmizer()
    pprint(po.getWeights(
                        # tickList=['JCI', 'TGT', 'CMCSA', 'CPB', 'MO', 'APA', 'MMC', 'JPM',
                        # 'ZION', 'PSA', 'BAX', 'BMY', 'LUV', 'PCAR', 'TXT', 'TMO',
                        # 'DE', 'MSFT', 'HPQ', 'SEE', 'VZ', 'CNP', 'NI', 'T', 'BA'],
                        filename='test.csv',obj='MaxRet',annualized_max_volatility=0.17))
