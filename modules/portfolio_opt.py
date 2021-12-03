import yfinance as yf

import pandas as pd

import riskfolio.Portfolio as pf
import riskfolio.PlotFunctions as plf

import numpy as np

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

class PortfolioOptmizer:

    def __init__(self):
        pass

    def getFromFile(self,filename):
        df = pd.read_csv(filename,index_col='Date')

        for col in df.columns[1:]:
            df = df.astype({col:'int32'})
        
        return df
    
    def weightsOptimizer(self,df):
        df = df.pct_change().dropna()
        port = pf(returns=df)
        port.assets_stats(method_mu='hist', method_cov='hist', d=0.94)

        model='Classic'
        rm = 'MV' 
        obj = 'Sharpe'
        hist = True 
        rf = 0
        l = 0

        w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)
        return np.array(w.T)[0]

    def piePlot(self,w,title = 'Sharpe Mean Variance',others=0.02,nrow=25,cmap='tab20',height=6,width=10,ax=None):
        ax = plf.plot_pie(w=w, title=title, others=others, nrow=nrow, cmap = cmap, height=height, width=width, ax=ax)
        plt.show()


    def getWeights(self,tickList=None,filename=None,lookBack='6mo'):
        
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
            
        weights = self.weightsOptimizer(df)
        self.piePlot(weights)


        return weights


if __name__=="__main__":
    po = PortfolioOptmizer()
    print(po.getWeights(tickList=['JCI', 'TGT', 'CMCSA', 'CPB', 'MO', 'APA', 'MMC', 'JPM',
                                  'ZION', 'PSA', 'BAX', 'BMY', 'LUV', 'PCAR', 'TXT', 'TMO',
                                  'DE', 'MSFT', 'HPQ', 'SEE', 'VZ', 'CNP', 'NI', 'T', 'BA'],
                                #   filename='test.csv'
                                  ))
