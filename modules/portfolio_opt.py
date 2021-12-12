from os import name
import yfinance as yf

import pandas as pd

from riskfolio import Portfolio
import riskfolio.PlotFunctions as plf
import riskfolio.RiskFunctions as rk

import numpy as np

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

from pprint import pprint
import random



import os

from multitasking import createPool
os.environ.setdefault("DJANGO_SETTINGS_MODULE","finserv.settings")

from datetime import datetime
from datetime import timedelta

import django 
# django.setup()


from portfolio import models as pModels



class PortfolioOptmizer:

    def __init__(self,tickList=None,filename=None,getFromDB=False):
        if getFromDB==True and tickList!=None:
            self.df = pd.DataFrame()

            for ticker in tickList:
                pass

        elif getFromDB==True and tickList==None:
            pass

        elif filename==None and tickList!=None:
            self.df = self.getFromNet(tickList)

        elif filename!=None and tickList==None:
            self.df = self.getFromFile(filename)

        else:
            raise Exception("Either filename or tickList must be provided.")

        self.portfolio = Portfolio(self.df.pct_change().dropna())
        self.portfolio.assets_stats(method_mu='hist', method_cov='hist', d=0.94)

        self.tickList = self.df.columns

        self.model='Classic'
        self.rm = 'MV' 
        self.hist = True 
        self.rf = 0
        self.l = 0

    def getFromFile(self,filename):
        df = pd.read_csv(filename,index_col='Date')
        for col in df.columns[1:]:
            df = df.astype({col:'int32'})
        return df
    



    def getFromNet(self,tickList,lookBack='6mo'):
        if lookBack not in ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']:
            raise Exception("lookBack must be one of the following\n'1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max'")
        
        df = pd.DataFrame()
        for ticker in tickList:
            tick = yf.Ticker(ticker)
            hist = tick.history(period=lookBack)
            df[ticker] = hist['Close']
        return df


    def cleanWeights(self):
        self.wCleaned = {x:round(y,4) for x,y in self.w.items() if round(y,4)!=0}

    def _weightsOptimizer(self,obj='Sharpe',annualized_min_return=None,annualized_max_volatility=None,t_factor=252):

        if annualized_min_return!=None and annualized_max_volatility==None:
            self.portfolio.lowerret=annualized_min_return/t_factor

        elif annualized_max_volatility!=None and annualized_min_return==None:
            self.portfolio.upperdev=annualized_max_volatility/t_factor**0.5

        self.wDF = self.portfolio.optimization(model=self.model, rm=self.rm, obj=obj, rf=self.rf, l=self.l, hist=self.hist)
        return {x:y for x,y in zip(self.tickList,np.array(self.wDF.T)[0])}




    def piePlot(self,title = 'Portfolio',others=0.02,nrow=25,cmap='tab20',height=6,width=10,ax=None):
        weights_df = pd.DataFrame.from_dict({x:[y] for x,y in self.w.items()},orient='index',columns=['weights'])
        ax = plf.plot_pie(w=weights_df, title=title, others=others, nrow=nrow, cmap = cmap, height=height, width=width, ax=ax)
        plt.show()

    def piePlotPlotly(self,name="Portfolio Composition"):
        

        fig = go.Figure(data=[go.Pie(labels=list(self.wCleaned.keys()), values=list(self.wCleaned.values()),textinfo='label+percent')])
        fig.update_traces(hole=.4, hoverinfo="percent+label")

        fig.show()

    def frontierPlot(self):
        w = pd.DataFrame.from_dict({x:[y] for x,y in self.w.items()},orient='index',columns=['weights'])

        points = 50
        frontier = self.portfolio.efficient_frontier(model=self.model, rm=self.rm, points=points, rf=self.rf, hist=self.hist)

        label = 'Max Risk Adjusted Return Portfolio'
        mu = self.portfolio.mu
        cov = self.portfolio.cov
        returns = self.portfolio.returns
        ax = plf.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=self.rm, rf=self.rf, alpha=0.05, cmap='viridis', w=w, label=label, marker='*', s=16, c='r', height=6, width=10, ax=None)
        plt.show()


    def frontierPlotPlotly(self,points=100,t_factor=252):
        X1 = []
        Y1 = []
        Z1 = []
        w_frontier = self.portfolio.efficient_frontier(model=self.model, rm=self.rm, points=points, rf=self.rf, hist=self.hist)


        for i in range(w_frontier.shape[1]):
            weights = np.array(w_frontier.iloc[:, i], ndmin=2).T
            risk = rk.Sharpe_Risk(
                weights, cov=self.portfolio.cov, returns=self.portfolio.returns, rm=self.rm, rf=self.rf, alpha=0.05
            )


            ret = 1 / self.portfolio.returns.shape[0] * np.sum(np.log(1 + self.portfolio.returns @ weights))
            ret = ret.item() * t_factor

            if self.rm not in ["MDD", "ADD", "CDaR", "EDaR", "UCI"]:
                risk = risk * t_factor ** 0.5

            ratio = (ret - self.rf) / risk

            X1.append(risk)
            Y1.append(ret)
            Z1.append(ratio)
        fig = px.scatter(x=X1, y=Y1, color=Z1)
        fig.show()



    def getWeights(self,obj='Sharpe',annualized_min_return=None,annualized_max_volatility=None):
        
        if annualized_min_return!=None and annualized_max_volatility==None:
            self.w = self._weightsOptimizer(obj=obj,annualized_min_return=annualized_min_return)

        elif annualized_max_volatility!=None and annualized_min_return==None:
            self.w = self._weightsOptimizer(obj=obj,annualized_max_volatility=annualized_max_volatility)
        elif obj=='Sharpe':
            self.w = self._weightsOptimizer(obj=obj)
        else:
            raise Exception("Either annualized_min_return or annualized_max_volatility must be provided...")

        self.cleanWeights()

        return self.w


    def getRiskStats(self,t_factor=252):
        returns = self.portfolio.returns['JCI']
        riskDict = {}
        sharpeRisk = rk.Sharpe_Risk(self.wDF, cov=self.portfolio.cov, returns=self.portfolio.returns, rm=self.rm, rf=self.rf, alpha=0.05)
        ann_vol = sharpeRisk*t_factor**0.5
        mad = rk.MAD(returns)
        semiDev = rk.SemiDeviation(returns)
        var = rk.VaR_Hist(returns)
        cvar = rk.CVaR_Hist(returns)
        wr = rk.WR(returns)
        lpm = rk.LPM(returns)
        entRM = rk.Entropic_RM(returns)
        evar = rk.EVaR_Hist(returns)
        mddAbs = rk.MDD_Abs(returns)
        addAbs = rk.ADD_Abs(returns)
        darAbs = rk.DaR_Abs(returns)
        cdarAbs = rk.CDaR_Abs(returns)
        edarAbs = rk.EDaR_Abs(returns)
        uciAbs = rk.UCI_Abs(returns)
        riskContrib = rk.Risk_Contribution(self.wDF,self.portfolio.cov,self.portfolio.returns)

        riskDict['ann_vol'] = ann_vol
        riskDict['sharpeRisk'] = sharpeRisk
        riskDict['mad'] = mad
        riskDict['semiDev'] = semiDev
        riskDict['var'] = var
        riskDict['cvar'] = cvar
        riskDict['wr'] = wr
        riskDict['lpm'] = lpm
        riskDict['entRM'] = entRM
        riskDict['evar'] = evar
        riskDict['mddAbs'] = mddAbs
        riskDict['addAbs'] = addAbs
        riskDict['darAbs'] = darAbs
        riskDict['cdarAbs'] = cdarAbs
        riskDict['edarAbs'] = edarAbs
        riskDict['uciAbs'] = uciAbs
        riskDict['riskContrib'] = riskContrib
        
        return riskDict


    def frontierAreaPlot(self,points=100):
        w_frontier = self.portfolio.efficient_frontier(model=self.model, rm=self.rm, points=points, rf=self.rf, hist=self.hist)
        
        fig = go.Figure()

        for i,row in w_frontier.iterrows():
            fig.add_trace(go.Scatter(
                x=list(range(points)), y=np.array(row),
                hoverinfo='x+y+name',
                mode='lines',
                line=dict(width=0.5, color='rgb({}, {}, {})'.format(random.randint(50,206),random.randint(50,206),random.randint(50,206))),
                stackgroup='one',
                name=i
            ))

        fig.update_layout(yaxis_range=(0, 1))
        fig.show()

    def dendrogramPlot(self):
        ax = plf.plot_dendrogram(returns=self.portfolio.returns, codependence='spearman',
                        linkage='ward', k=None, max_k=10,
                        leaf_order=True, ax=None)
        plt.show()

    def clusterPlot(self):
        ax = plf.plot_clusters(returns=self.portfolio.returns, codependence='spearman',
                      linkage='ward', k=None, max_k=10,
                      leaf_order=True, dendrogram=True, ax=None)

        plt.show()
if __name__=="__main__":
    po = PortfolioOptmizer(
                            # tickList=['JCI', 'TGT', 'CMCSA', 'CPB', 'MO', 'APA', 'MMC', 'JPM',
                            # 'ZION', 'PSA', 'BAX', 'BMY', 'LUV', 'PCAR', 'TXT', 'TMO',
                            # 'DE', 'MSFT', 'HPQ', 'SEE', 'VZ', 'CNP', 'NI', 'T', 'BA'],
                            filename='test.csv',getFromDB=False
                        )
    pprint(po.getWeights(obj='MaxRet',annualized_max_volatility=0.17))
    po.clusterPlot()
