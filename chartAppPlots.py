#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 23:05:15 2018

@author: Thomas Atta-Fosu (attafosu@yahoo.com)
"""

import pandas as pd
import datetime
import numpy as np
from matplotlib import pylab as plt
from matplotlib import dates as mdates
from dateutil import relativedelta

#%% Recession Months
Recessions = {1949: (datetime.date(1948, 11, 30), datetime.date(1949, 10, 1)),
              1953: (datetime.date(1953, 7, 31), datetime.date(1954, 5, 1)),
              1958: (datetime.date(1957, 8, 31), datetime.date(1958, 4, 1)),
              1960: (datetime.date(1960, 4, 30), datetime.date(1961, 2, 1)),
              1969: (datetime.date(1969, 12, 31), datetime.date(1970, 11, 1)),
              1973: (datetime.date(1973, 11, 30), datetime.date(1975, 3, 1)),
              1980: (datetime.date(1980, 1, 31), datetime.date(1980, 7, 1)),
              1981: (datetime.date(1981, 7, 31), datetime.date(1982, 11, 1)),
              1990: (datetime.date(1990, 7, 31), datetime.date(1991, 3, 1)),
              2001: (datetime.date(2001, 3, 31), datetime.date(2001, 11, 1)),
              2007: (datetime.date(2007, 12, 31), datetime.date(2009, 6, 1))}

#%% Graph class
class DoubleLineGraphs:

    def __init__(self, data_path):
        self.Recessions = Recessions
        
        self.data = data_path
        xls = pd.ExcelFile(self.data)
#        try:
#            xls = pd.ExcelFile(self.data)
#        except:
#            print("Cannot open file. Make sure file exists")
#            return
#        
        try:
            self.LEI = xls.parse("LEI Year over Year Change").get_values()
        except:
            print("Spreadsheet does not have sheet named 'LEI Year over Year Change'. Cannot plot LEI graphs")
        
        self.PMI = xls.parse('PMI',header=None).get_values()
        self.CC = xls.parse('Consumer Confidence',header=None).get_values() #Consumer Confidence
        self.CEOC = xls.parse('CEO Confidence',header=None).get_values() # CEO Confidence
        self.HBC = xls.parse('Home Builder Confidence',header=None).get_values()
        self.SBO = xls.parse('Small Business Optimism',header=None).get_values()
        self.HYS = xls.parse('HY Spreads',header=None).get_values()
        self.CPI = xls.parse('Core CPI',header=None).get_values()
        self.GDP = xls.parse('Real GDP YoY',header=None).get_values()
        self.NYFED = xls.parse('New York Fed Underlying Inf',header=None).get_values()
        self.CU = xls.parse('Capacity Utilization',header=None).get_values()

#%%        
    def coreCPIvCapacityUtil(self, cpi_start_date=datetime.date(1998, 1,1),
                             cu_lag_months = 1):
        cu_start_date = cpi_start_date - relativedelta.relativedelta(months=cu_lag_months)
        
        cu = {}
        cpi = {}
        
        for ss in range(self.CU.shape[0]):
            date = self.CU[ss,0]
            if not isinstance(date,datetime.date) or date.date() < cu_start_date:
                continue
            
            lag_date = date + relativedelta.relativedelta(months=16)
            cu[lag_date] = self.CU[self.CU[:,0]==date,1][0]
            
        for ss in range(self.CPI.shape[0]):
            date = self.CPI[ss,0]
            if not isinstance(date, datetime.date) or date.date() < cpi_start_date:
                continue
            
            cpi[date] = self.CPI[self.CPI[:,0]==date,1][0]
            
            
        lcpi = sorted(cpi.items())
        lcu = sorted(cu.items())
        
        xcpi, ycpi = zip(*lcpi)
        xcu, ycu = zip(*lcu)
        self.xcpi , self.ycpi = xcpi, ycpi
        self.xcu, self.ycu = xcu, ycu
        
        
        ser_cpi = pd.Series(ycpi, index=xcpi)
        ser_cu = pd.Series(ycu, index=xcu)
        
        res_cpi = ser_cpi.resample('D').interpolate(method='linear')
        res_cu = ser_cu.resample('D').interpolate(method='linear')

        start_date = max([min(res_cpi.index),min(res_cu.index)])
        end_date = min([max(res_cpi.index),max(res_cu.index)]) 
        
        self.res_cpi = res_cpi.loc[start_date:end_date]
        self.res_cu = res_cu.loc[start_date:end_date]
#        self.res_cpi.plot()
        
        self.cpi_caputil_cor = np.corrcoef(self.res_cpi, self.res_cu)
        
    #%% CPI vs PMI
    def coreCPIvsISMPMI(self, cpi_start_date = datetime.date(1998, 1, 1), pmi_lag_months=21):
        self.pmi = {}
        self.cpi = {}
        
        pmi_start_date = cpi_start_date - relativedelta.relativedelta(months=pmi_lag_months)
        
        for ss in range(self.PMI.shape[0]):
            date = self.PMI[ss,0]
            if not isinstance(date,datetime.date) or date.date() < pmi_start_date:
                continue
            
            lag_date = date + relativedelta.relativedelta(months=23)
            self.pmi[lag_date] = self.PMI[self.PMI[:,0]==date,1][0]
            
        for ss in range(self.CPI.shape[0]):
            date = self.CPI[ss,0]
            if not isinstance(date, datetime.date) or date.date() < cpi_start_date:
                continue
            
            self.cpi[date] = self.CPI[self.CPI[:,0]==date,1][0]
            
        lcpi = sorted(self.cpi.items())
        lpmi = sorted(self.pmi.items())
        
        self.xcpi, self.ycpi = zip(*lcpi)
        
        self.xpmi, self.ypmi = zip(*lpmi)
        
        imdates = set(self.xcpi).intersection(self.xpmi)
        
        ser_cpi = pd.Series(self.ycpi, index=self.xcpi)
        ser_pmi = pd.Series(self.ypmi, index=self.xpmi)
        
#        res_cpi = ser_cpi.resample('3D').interpolate(method='linear')
#        res_pmi = ser_pmi.resample('3D').interpolate(method='linear')
#
#        start_date = max([min(res_cpi.index),min(res_pmi.index)])
#        end_date = min([max(res_cpi.index),max(res_pmi.index)]) 
        
        self.res_cpi = ser_cpi.loc[imdates]
        self.res_pmi = ser_pmi.loc[imdates]
#        self.res_pmi.plot()
        
        self.cpi_pmi_cor = np.corrcoef(self.res_cpi, self.res_pmi)   
    #%%        
    def confidenceScores(self,):
        ncc = {}
        nceoc = {}
        nhbc = {}
        nsbo = {}
        meanConf = {}
        
        self.zcc = {}
        self.zceoc = {}
        self.zhbc = {}
        self.zsbo = {}
        self.zmeanconf = {}
        
        for ss in range(self.CEOC.shape[0]):
            date = self.CEOC[ss,0]
            if not isinstance(date,datetime.date):
                continue
            
            cc = self.CC[self.CC[:,0]==date,1][0]
            ceoc = 10*self.CEOC[self.CEOC[:,0]==date,1][0]
            hbc = self.HBC[self.HBC[:,0]==date,1][0]
            sbo = self.SBO[self.SBO[:,0]==date,1][0]
            
            meanConf[date] = np.mean(np.asarray([cc,ceoc,hbc,sbo]))            
            ncc[date] = cc
            nceoc[date] = ceoc
            nhbc[date] = hbc
            nsbo[date] = sbo

        for date in ncc.keys():
            
            
            cc = (ncc[date] - np.mean(list(ncc.values())))/np.std(list(ncc.values()))
            ceoc = (nceoc[date] - np.mean(list(nceoc.values())))/np.std(list(nceoc.values()))
            hbc = (nhbc[date] - np.mean(list(nhbc.values())))/np.std(list(nhbc.values()))
            sbo = (nsbo[date] - np.mean(list(nsbo.values())))/np.std(list(nsbo.values()))
                        
            self.zmeanconf[date] = np.mean(np.asarray([cc,ceoc,hbc,sbo]))            
            self.zcc[date] = cc
            self.zceoc[date] = ceoc
            self.zhbc[date] = hbc
            self.zsbo[date] = sbo
            
            
    #%%
    def HighYeildSpread(self, scope, data_end_date=datetime.date(2018, 4, 17)):
        # scope ---> How far out to track (for High yield spreads, this is no. of days)
        # data_end_date ----> Latest month       
#        trending_year_start_date = data_end_date.replace(year=data_end_date.year-1) # 1 year ago
        #print("data_end_date: {}".format(data_end_date))
#        current_1year_trend = {} # to store the preceding year's data    
        self.HYscope = scope
        self.one_year_to_recession = {}
        self.six_mos_to_recession = {}
        self.recession_2001 = {}
        self.recession_2007 = {}
        
        for d in range(1,self.HYS.shape[0]):
            
            day = self.HYS[d,0]
            
            if isinstance(day,float):
                continue
            
            if 'Date' in day:
                continue
            
            if '/' not in day:
                continue
            
            
            #ymd = day.split('/')
            date = datetime.datetime.strptime(day,'%m/%d/%Y').date()#datetime.date(int(ymd[2]), int(ymd[0]), int(ymd[1]))
            # Saving past year trends
            
            if abs((Recessions[2001][0] - date).days) < scope:
                timediff2001 = (date - Recessions[2001][0]).days           
                self.recession_2001[timediff2001] = self.HYS[self.HYS[:,0]==day, 1][0]
                
            elif abs((Recessions[2007][0] - date).days) < scope:
                timediff2007 = (date - Recessions[2007][0]).days
                self.recession_2007[timediff2007] = self.HYS[self.HYS[:,0]==day, 1][0]
            else:
                timediff = (data_end_date - date).days
                if (timediff < scope) and (timediff > 120):           
                    self.six_mos_to_recession[-timediff] =  self.HYS[self.HYS[:,0]==day, 1][0]
            
                if (timediff <=365) and (timediff>120):
                    self.one_year_to_recession[-timediff] = self.HYS[self.HYS[:,0]==day, 1][0]            
                    
    #%% Leading Economic Indicator
    def leadingEconomicIndicators(self,scope, trending_year=1):
        # scope ---> How far out to track
        # trending_year ---> current period in perspective
        
        months_to_and_after = dict((el, []) for el in range(-scope, scope+1, 1)) # To store the leadinng months
        
        end_date = datetime.datetime(1920,1,1,0,0) # To get end date
        for year in Recessions.keys():
            
            start_date = Recessions[year][0]
            
            for d in range(self.LEI.shape[0]):
                date = self.LEI[d,0]
                if not isinstance(date,datetime.date):
                    continue
                    
                if abs((date.date() - start_date)).days <= (scope)*31:
                    timediff = (date.date() - start_date).days
                    if abs(timediff)<155:
                        timediff = np.sign(timediff)*round((abs(timediff)/28))
                    else:
                        timediff = np.sign(timediff)*round((abs(timediff)/30))
#                    if timediff==0:
#                        print(date)
                    val = self.LEI[self.LEI[:,0]==date, 1]
                    months_to_and_after[timediff].append( val[0] )
                    
                if end_date < date:
                    end_date = date
        #%%  Do some stats
        # stats are 25th percentile, mean and 75th percentile 
        mean_vals = {}
        prctile_25 = {}
        prctile_75 = {}
        
        for lag_month in months_to_and_after.keys():
            vals = np.asarray(months_to_and_after[lag_month])
            mean_vals[lag_month] = np.mean(vals)
            prctile_25[lag_month] = np.percentile(vals, 25)
            prctile_75[lag_month] = np.percentile(vals, 75)
                
        #%% Current year trend stats
        data_end_date = end_date#self.LEI[self.LEI[:,0]=='End Date',1][0] # Get latest month 
        
        trending_year_start_date = data_end_date.replace(year=data_end_date.year-trending_year) # tracking period ago
        
        current_1year_trend = {} # to store the preceding year's data    
        
        for d in range(self.LEI.shape[0]):
            date = self.LEI[d,0]
            if not isinstance(date,datetime.date):
                continue
            
            # Saving past year trends
            if (date <= data_end_date) and (date >= trending_year_start_date):
                timediff = (data_end_date - date).days
                if timediff<155:
                    timediff = np.sign(timediff)*(abs(timediff)/28)
                else:
                    timediff = np.sign(timediff)*(abs(timediff)/30)
        
                # subtract 12 if you do 
                current_1year_trend[-timediff-12] = self.LEI[self.LEI[:,0]==date, 1][0]
                
                
        self.leimean = sorted(mean_vals.items())
        self.lei25 = sorted(prctile_25.items())
        self.lei75 = sorted(prctile_75.items())        
        self.leicurr = sorted(current_1year_trend.items())
        
        
    #%% ISM PMI leading to recession
    def pmiLeadingToRecession(self, scope, trending_year=1):
        # scope ---> How far out to track
        # trending_year ---->  current period in focus
        
        months_to_and_after = dict((el, []) for el in range(-scope, scope+1, 1)) # To store the leadinng months
        
        end_date = datetime.datetime(1920,1,1,0,0)
        for year in Recessions.keys():
            
            start_date = Recessions[year][0]
            
            for d in range(self.PMI.shape[0]):
                date = self.PMI[d,0]
                if not isinstance(date,datetime.date):
                    continue
                    
                if abs((date.date() - start_date)).days <= (scope)*31:
                    timediff = (date.date() - start_date).days
                    if abs(timediff)<155:
                        timediff = np.sign(timediff)*round((abs(timediff)/28))
                    else:
                        timediff = np.sign(timediff)*round((abs(timediff)/30))
                        
#                    if timediff==0:
#                        print(date)
                    val = self.PMI[self.PMI[:,0]==date, 1]
                    months_to_and_after[timediff].append( val[0] )
                    
                if end_date < date:
                    end_date = date
                    
            
        #%%  Do some stats
        # stats are 25th percentile, mean and 75th percentile 
        mean_vals = {}
        prctile_25 = {}
        prctile_75 = {}
        
        for lag_month in months_to_and_after.keys():
            vals = np.asarray(months_to_and_after[lag_month])
            mean_vals[lag_month] = np.mean(vals)
            prctile_25[lag_month] = np.percentile(vals, 25)
            prctile_75[lag_month] = np.percentile(vals, 75)

        
        #%% Current year trend stats
        data_end_date = end_date#self.PMI[self.PMI[:,0]=='End Date',1][0] # Get latest month 
        
        trending_year_start_date = data_end_date.replace(year=data_end_date.year-1) # 1 year ago
        
        current_1year_trend = {} # to store the preceding year's data    
        
        for d in range(self.PMI.shape[0]):
            date = self.PMI[d,0]
            if not isinstance(date,datetime.date):
                continue
            
            # Saving past year trends
            if (date <= data_end_date) and (date >= trending_year_start_date):
                timediff = (data_end_date - date).days
                if timediff<155:
                    timediff = np.sign(timediff)*(abs(timediff)/28)
                else:
                    timediff = np.sign(timediff)*(abs(timediff)/30)
        
                current_1year_trend[-timediff-12] = self.PMI[self.PMI[:,0]==date, 1][0]
        
        self.pmimean = sorted(mean_vals.items())
        self.pmi25 = sorted(prctile_25.items())
        self.pmi75 = sorted(prctile_75.items())
        self.pmicurr = sorted(current_1year_trend.items())
        
#%%        
    def coreCPIvsNYFED(self, cpi_start_date=datetime.date(1998, 1, 1), nyfed_lag_months=16):
        
        nyfed_start_date = cpi_start_date - relativedelta.relativedelta(months=16)

        nyfed = {}
        cpi = {}
        
        for ss in range(self.NYFED.shape[0]):
            date = self.NYFED[ss,0]
            if not isinstance(date,datetime.date) or date.date() < nyfed_start_date:
                continue
            
            lag_date = date + relativedelta.relativedelta(months=16)
            nyfed[lag_date] = self.NYFED[self.NYFED[:,0]==date,1][0]
            
        for ss in range(self.CPI.shape[0]):
            date = self.CPI[ss,0]
            if not isinstance(date, datetime.date) or date.date() < cpi_start_date:
                continue
            
            cpi[date] = self.CPI[self.CPI[:,0]==date,1][0]
            
            
        self.lcpi = sorted(cpi.items())
        self.lnyfed = sorted(nyfed.items())
        
        xcpi, ycpi = zip(*self.lcpi)        
        xnyfed, ynyfed = zip(*self.lnyfed)        
        
        self.xcpi , self.ycpi = xcpi, ycpi
        self.xnyfed, self.ynyfed = xnyfed, ynyfed
        
        
        ser_cpi = pd.Series(ycpi, index=xcpi)
        ser_nyfed = pd.Series(ynyfed, index=xnyfed)
        
        res_cpi = ser_cpi.resample('D').interpolate(method='linear')
        res_nyfed = ser_nyfed.resample('D').interpolate(method='linear')

        start_date = max([min(res_cpi.index),min(res_nyfed.index)])
        end_date = min([max(res_cpi.index),max(res_nyfed.index)]) 
        
        self.res_cpi = res_cpi.loc[start_date:end_date]
        self.res_nyfed = res_nyfed.loc[start_date:end_date]
#        self.res_cpi.plot()
        
        self.cpi_nyfed_cor = np.corrcoef(self.res_cpi, self.res_nyfed)

        
    def coreCPIvsGDP(self,cpi_start_date=datetime.date(1998, 1, 1)):
        gdp_start_date = cpi_start_date - relativedelta.relativedelta(months=23)
        
        gdp = {}
        cpi = {}
        
        for ss in range(self.GDP.shape[0]):
            date = self.GDP[ss,0]
            if not isinstance(date,datetime.date) or date.date() < gdp_start_date:
                continue
            
            lag_date = date + relativedelta.relativedelta(months=16)
            gdp[lag_date] = self.GDP[self.GDP[:,0]==date,1][0]
            
        for ss in range(self.CPI.shape[0]):
            date = self.CPI[ss,0]
            if not isinstance(date, datetime.date) or date.date() < cpi_start_date:
                continue
            
            cpi[date] = self.CPI[self.CPI[:,0]==date,1][0]
            
            
        self.lcpi = sorted(cpi.items())
        self.lgdp = sorted(gdp.items())
        
        xcpi, ycpi = zip(*self.lcpi)
        xgdp, ygdp = zip(*self.lgdp)
        
        self.xcpi , self.ycpi = xcpi, ycpi
        self.xgdp, self.ygdp = xgdp, ygdp
        
        
        ser_cpi = pd.Series(ycpi, index=xcpi)
        ser_gdp = pd.Series(ygdp, index=xgdp)
        
        res_cpi = ser_cpi.resample('D').interpolate(method='linear')
        res_gdp = ser_gdp.resample('D').interpolate(method='linear')

        start_date = max([min(res_cpi.index),min(res_gdp.index)])
        end_date = min([max(res_cpi.index),max(res_gdp.index)]) 
        
        self.res_cpi = res_cpi.loc[start_date:end_date]
        self.res_gdp = res_gdp.loc[start_date:end_date]
#        self.res_cpi.plot()
        
        self.cpi_gdp_cor = np.corrcoef(self.res_cpi, self.res_gdp)

#%% Plot
    def plotCPIvsGDP(self, cpi_start_date=datetime.date(1998, 1, 1)):
        self.coreCPIvsGDP(cpi_start_date=cpi_start_date)
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        
        xcpi, ycpi = zip(*self.lcpi)
        xgdp, ygdp = zip(*self.lgdp)
        
        gdp_curve, = ax.plot(xgdp,ygdp,lw=3,color='r',alpha=1, label='Real GDP (YoY)')
        
        ax2 = ax.twinx()
        cpi_curve, = ax2.plot(xcpi,ycpi,lw=3,color='b',alpha=0.9,label='CPI (YoY)')
        
        ax.tick_params(labelsize=20)
        ax2.tick_params(labelsize=20)
        
        ax.tick_params(axis='y', colors=gdp_curve.get_color())
        ax2.tick_params(axis='y', colors=cpi_curve.get_color())
        
        ybounds = ax.get_ybound()
        
        ax.fill_betweenx(ybounds,Recessions[2001][0], Recessions[2001][1] ,color='r',alpha=0.3)
        shade = ax.fill_betweenx(ybounds,Recessions[2007][0], Recessions[2007][1] ,color='r',alpha=0.3,label='recession')
        
        lines = [gdp_curve, cpi_curve, shade]
        ax.legend(lines, [l.get_label() for l in lines], loc='lower right', fontsize=25)
        ax.set_title('Core CPI and Real GDP (16mo Lead): Corr = {}'.format(round(self.cpi_gdp_cor[0,1],3)),fontsize=25)
        
        return fig
#%% Plot
    def plotCPIvsNYFED(self):
        self.coreCPIvsNYFED()
        xcpi, ycpi = zip(*self.lcpi)        
        xnyfed, ynyfed = zip(*self.lnyfed)
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
               
        nyfed_curve, = ax.plot(xnyfed,ynyfed,lw=3,color='r',alpha=1, label='NY Fed Inflation')
        
        ax2 = ax.twinx()
        cpi_curve, = ax2.plot(xcpi,ycpi,lw=3,color='b',alpha=0.9,label='CPI (YoY)')
        
        ax.tick_params(labelsize=20)
        ax2.tick_params(labelsize=20)
        
        ax.tick_params(axis='y', colors=nyfed_curve.get_color())
        ax2.tick_params(axis='y', colors=cpi_curve.get_color())
        
        ybounds = ax.get_ybound()
        
        ax.fill_betweenx(ybounds,Recessions[2001][0], Recessions[2001][1] ,color='r',alpha=0.3)
        shade = ax.fill_betweenx(ybounds,Recessions[2007][0], Recessions[2007][1] ,color='r',alpha=0.3,label='recession')
        
        lines = [nyfed_curve, cpi_curve, shade]
        ax.legend(lines, [l.get_label() for l in lines], loc='lower right', fontsize=25)
        ax.set_title('Core CPI and NY Fed Inflation (16mo Lead): Corr = {}'.format(round(self.cpi_nyfed_cor[0,1],3)),fontsize=25)
        
        return fig
        #%% Plot confidence scores
    def plotConfidenceScores(self):
        self.confidenceScores()
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        lhbc = sorted(self.zhbc.items())
        lceoc = sorted(self.zceoc.items())
        lsbo = sorted(self.zsbo.items())
        lcc= sorted(self.zcc.items())
        lmean = sorted(self.zmeanconf.items())
        
        xcc,ycc = zip(*lcc)
        xhbc,yhbc = zip(*lhbc)
        xceoc, yceoc = zip(*lceoc)
        xsbo, ysbo = zip(*lsbo)
        xmean, ymean = zip(*lmean)
        
        ax.plot(xcc,ycc,lw=3,color='blue')
        ax.plot(xceoc, yceoc,color='red',lw=3)
        ax.plot(xhbc, yhbc, color='orange',lw=3)
        ax.plot(xsbo, ysbo, color='green',lw=3)
        ax.plot(xmean, ymean, color='black',lw=3)
        
        ax.grid(axis='y')
        ax.set_ylabel('z-score',fontsize=20)
        ax.set_ylim(-4,3)
        ax.tick_params(labelsize=20)
        
        recession = Recessions[2007]
        ax.fill_betweenx([-4,3], recession[0], recession[1], color='gray',alpha=0.5)
        
        ax.legend(['Consumer Conf','CEO Conf','Home Builders Conf','Small Busi Opt.', 'Average','Recession'],fontsize=18)
                
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
        plt.gcf().autofmt_xdate()
        
        return fig
    #%%    
    def plotDummyCPIvCapacityUtil(self):
        self.coreCPIvCapacityUtil()
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        
        
#        print(self.cpi_caputil_corr)
        
        
        cu_curve, = ax.plot(self.res_cu.index, self.res_cu.values,lw=3,color='r',alpha=1, label='Capacity Util.')
        
        ax2 = ax.twinx()
        cpi_curve, = ax2.plot(self.res_cpi.index, self.res_cpi.values,lw=3,color='b',alpha=0.9,label='CPI (YoY)')
        
        ax.tick_params(labelsize=20)
        ax2.tick_params(labelsize=20)
        
        ax.tick_params(axis='y', colors=cu_curve.get_color())
        ax2.tick_params(axis='y', colors=cpi_curve.get_color())
        
        ybounds = ax.get_ybound()
        
        ax.fill_betweenx(ybounds, self.Recessions[2001][0], self.Recessions[2001][1],
                         color='r',alpha=0.3)
        shade = ax.fill_betweenx(ybounds, self.Recessions[2007][0], self.Recessions[2007][1],
                                 color='r',alpha=0.3,label='recession')
        
        lines = [cu_curve, cpi_curve, shade]
        ax.legend(lines, [l.get_label() for l in lines], loc='lower right', fontsize=25)
        ax.set_title('Core CPI and Capacity Utilization: Corr = {}'.format(round(self.cpi_caputil_cor[0,1],3)),fontsize=25)
        
    
        return fig   
#%%    
    def plotCPIvCapacityUtil(self):
        self.coreCPIvCapacityUtil()
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        
        
#        print(self.cpi_caputil_corr)
        
        
        cu_curve, = ax.plot(self.xcu, self.ycu,lw=3,color='r',alpha=1, label='Capacity Util.')
        
        ax2 = ax.twinx()
        cpi_curve, = ax2.plot(self.xcpi, self.ycpi,lw=3,color='b',alpha=0.9,label='CPI (YoY)')
        
        ax.tick_params(labelsize=20)
        ax2.tick_params(labelsize=20)
        
        ax.tick_params(axis='y', colors=cu_curve.get_color())
        ax2.tick_params(axis='y', colors=cpi_curve.get_color())
        
        ybounds = ax.get_ybound()
        
        ax.fill_betweenx(ybounds, self.Recessions[2001][0], self.Recessions[2001][1],
                         color='r',alpha=0.3)
        shade = ax.fill_betweenx(ybounds, self.Recessions[2007][0], self.Recessions[2007][1],
                                 color='r',alpha=0.3,label='recession')
        
        lines = [cu_curve, cpi_curve, shade]
        ax.legend(lines, [l.get_label() for l in lines], loc='lower right', fontsize=25)
        ax.set_title('Core CPI and Capacity Utilization (16mo Lead): Corr = {}'.format(round(self.cpi_caputil_cor[0,1],3)),fontsize=25)
        
    
        return fig      
        #%% Plot
    def plotCPIvsPMI(self):
        self.coreCPIvsISMPMI()
        
        lcpi = sorted(self.cpi.items())
        lpmi = sorted(self.pmi.items())
        
        xcpi, ycpi = zip(*lcpi)
        
        xpmi, ypmi = zip(*lpmi)
             
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
                
        
        
        pmi_curve, = ax.plot(xpmi,ypmi,lw=3,color='r',alpha=1, label='ISM PMI')
        
        ax2 = ax.twinx()
        cpi_curve, = ax2.plot(xcpi,ycpi,lw=3,color='b',alpha=0.9,label='CPI (YoY)')
        
        ax.tick_params(labelsize=20)
        ax2.tick_params(labelsize=20)
        
        ax.tick_params(axis='y', colors=pmi_curve.get_color())
        ax2.tick_params(axis='y', colors=cpi_curve.get_color())
        
        ybounds = ax.get_ybound()
        
        ax.fill_betweenx(ybounds,Recessions[2001][0], Recessions[2001][1] ,color='r',alpha=0.3)
        shade = ax.fill_betweenx(ybounds,Recessions[2007][0], Recessions[2007][1] ,color='r',alpha=0.3,label='recession')
        
        lines = [pmi_curve, cpi_curve, shade]
        ax.legend(lines, [l.get_label() for l in lines], loc='lower right', fontsize=25)
        ax.set_title('Core CPI and ISM PMI (23mo Lead): Corr = {}'.format(round(self.cpi_pmi_cor[0,1],3)),fontsize=25)
    
        return fig

    def plotDummyCPIvsPMI(self):
        self.coreCPIvsISMPMI()
        
        lcpi = sorted(self.cpi.items())
        lpmi = sorted(self.pmi.items())
        
        xcpi, ycpi = zip(*lcpi)
        
        xpmi, ypmi = zip(*lpmi)
             
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
                
        
        ax.scatter(self.res_cpi.values, self.res_pmi.values,s=10)
#        pmi_curve, = ax.plot(self.res_pmi.index, self.res_pmi.values,lw=3,color='r',alpha=1, label='ISM PMI')
#        
#        ax2 = ax.twinx()
#        cpi_curve, = ax2.plot(self.res_cpi.index,self.res_cpi.values,lw=3,color='b',alpha=0.9,label='CPI (YoY)')
#        
#        ax.tick_params(labelsize=20)
#        ax2.tick_params(labelsize=20)
#        
#        ax.tick_params(axis='y', colors=pmi_curve.get_color())
#        ax2.tick_params(axis='y', colors=cpi_curve.get_color())
#        
#        ybounds = ax.get_ybound()
#        
#        ax.fill_betweenx(ybounds,Recessions[2001][0], Recessions[2001][1] ,color='r',alpha=0.3)
#        shade = ax.fill_betweenx(ybounds,Recessions[2007][0], Recessions[2007][1] ,color='r',alpha=0.3,label='recession')
#        
#        lines = [pmi_curve, cpi_curve, shade]
#        ax.legend(lines, [l.get_label() for l in lines], loc='lower right', fontsize=25)
#        ax.set_title('Core CPI and ISM PMI: Corr = {}'.format(round(self.cpi_pmi_cor[0,1],3)),fontsize=25)
#    
        return fig        
    #%% Plots
    def plotHighYeild(self):
        
        
        #dates=[datetime.date(int(el.split('/')[2]), int(el.split('/')[0]), int(el.split('/')[1])) for el in self.HYS[2:,0] if ((not isinstance(el, float)) and ('/' in el) and (len(el)<15) )]
        entry = self.HYS[4,0]
        if isinstance(entry, datetime.date):
            end_date=entry
        else:
            try:
                end_date=datetime.datetime.strptime(entry,'%m/%d/%Y').date()
            except TypeError:
                print("Cannot parse '{}' as date. Check entry 5 of 'HY Spreads'. See 'plotHighYield' method in 'ChartAppPlots.py' to change end_date'".format(entry))            
        
        #print("End date: {}".format(end_date))
        self.HighYeildSpread(scope=600, data_end_date=end_date)
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        
        #%%
        l2001 = sorted(self.recession_2001.items())
        l2007 = sorted(self.recession_2007.items())
        l6mo = sorted(self.six_mos_to_recession.items())
        l1yr = sorted(self.one_year_to_recession.items())
        
        x2001, y2001 = zip(*l2001)
        x2007, y2007 = zip(*l2007)
        x6mo, y6mo = zip(*l6mo)
        x1yr, y1yr = zip(*l1yr)        
        
        ax.plot(x2001, y2001,lw=3,color='b',alpha=0.9)
        ax.plot(x2007, y2007,lw=3,color='yellow',alpha=0.9)
        ax.plot(x6mo, y6mo,lw=3,color='k',alpha=0.9)
        ax.plot(x6mo[:len(x1yr)], y1yr,lw=3,color='g',alpha=0.9)
        
        ax.grid(axis='y')
        
        ybounds = ax.get_ybound()
        
        ax.fill_betweenx(ybounds, 1,self.HYscope, alpha=0.5)
        
        xticks = range(-self.HYscope,self.HYscope,40)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks)
        ax.set_yticklabels([0,5,10,15,20])
        
        #ax.set_ylabel('YoY (%)',fontsize=20)
        ax.set_xlabel('Trading Days to Recession',fontsize=20)
        ax.tick_params(labelsize=20)
        
        ax.legend(['2001', '2007', 'Now (6mo to Recession)', 'Now (1yr to Recession)', 'Recession'],fontsize=25)
        ax.set_xlim(-self.HYscope-2, self.HYscope+5)
        plt.xticks(rotation='vertical')
        return fig

    #%%
    def plotLEI(self):
        self.leadingEconomicIndicators(24)
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        
        xmean,ymean = zip(*self.leimean)
        x25, y25 = zip(*self.lei25)
        x75, y75 = zip(*self.lei75)
        mons, vals = zip(*self.leicurr)
        
        months_to_ = x25[:len(vals)]
        ax.grid(axis='y')
        
        ax.fill_between(x25, y25, y75, alpha=0.5,linewidth=1,linestyle='dashed',edgecolor='r')
        
        ax.plot(months_to_,vals,lw=3,color='b',alpha=0.9)
        
        xticks = [-24,-20,-16,-12,-8,-4,0,4,8,12,16,20,24]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks)
        
        ax.set_ylabel('LEI YoY (%)',fontsize=20)
        ax.set_xlabel('Months Leading up to Recession',fontsize=20)
        ax.tick_params(labelsize=20)
        
        ybounds = ax.get_ybound()
        xbounds = ax.get_xbound()
        ax.legend(['Current (1yr to Rec.)', '25th/75th %le'], fontsize=25, loc='lower left')
        ax.set_xlim(xmean[0]-.5, xmean[-1]+.5)
        ax.vlines(0, ybounds[0], ybounds[1], linestyle='dashed',lw=3)
        ax.hlines(0, xmean[0], xbounds[1], lw=3,color='gray')
        
        return fig
        #%% Plots
    def plotPMItoRecession(self):
        self.pmiLeadingToRecession(24)
        
        fig = plt.figure(figsize=(15,7))
        ax = fig.add_subplot(111)
        
        xmean,ymean = zip(*self.pmimean)
        x25, y25 = zip(*self.pmi25)
        x75, y75 = zip(*self.pmi75)
        months_to, vals = zip(*self.pmicurr)
        
        ax.plot(months_to,vals,lw=3,color='k',alpha=0.9)
        ax.grid(axis='y')
        
        
        ax.fill_between(x25, y25, y75, alpha=0.5,linewidth=1,linestyle='dashed',edgecolor='r')
        
        xticks = [-24,-20,-16,-12,-8,-4,0,4,8,12,16,20,24]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks)
        
        ax.set_ylabel('PMI YoY (%)',fontsize=20)
        ax.set_xlabel('Months Leading up to Recession',fontsize=20)
        ax.tick_params(labelsize=20)
        
        ybounds = ax.get_ybound()
        ax.legend(['Current (1yr to Rec.)', '25th/75th %le'], fontsize=25,loc='lower left')
        ax.set_xlim(xmean[0]-.5, xmean[-1]+.5)
        ax.vlines(0, ybounds[0], ybounds[1], linestyle='dashed',lw=3)
        
        return fig

