import pandas as pd
import streamlit as st


#sim_start='2020-10-01'
#end_date='2022-10-27'
#n_days_measure_perf=100
#top_n_stocks=10
#in_eq=1000000

st.title('Stock Simulation')

sim_start=st.text_input('Start Date')
end_date=st.text_input('End Date')
n_days_measure_perf=st.text_input('n days measure stock')
top_n_stocks=st.text_input('Top n stocks')
in_eq=st.text_input('Initial Investment')


df = pd.read_csv('https://archives.nseindia.com/content/indices/ind_nifty50list.csv')
nifty_list=df['Symbol'].tolist()

d={}                            #dictionary of dataframes
for x in range(0,50):           #Collecting data from all the Nifty stocks
    d[nifty_list[x]]=pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/' + nifty_list[x] + '.NS?period1=1601510400&period2=1687219200&interval=1d&events=history&includeAdjustedClose=true')

datefilter = (d['APOLLOHOSP']['Date'] >= sim_start) & (d['APOLLOHOSP']['Date'] <= end_date)  #define date filter with Apollo hospital as reference
    
for x in range(0,50):
    d[nifty_list[x]] = d[nifty_list[x]].loc[datefilter]


#benchmark
for x in range(0,50):                                               #daily value for each stock            
    d[nifty_list[x]]['DailyVal{0}'.format(x)] = (in_eq/50) / (d[nifty_list[x]]['Open'].loc[d[nifty_list[x]].index[0]]) * (d[nifty_list[x]]['Close'])
                                                        #initial investment on each stock / initial price of stock{day 1 opening} * closing value of each day

equitytablebench=pd.DataFrame()

for x in range(0,50):               #concatenating daily value columns from each stock
    equitytablebench = pd.concat([equitytablebench, d[nifty_list[x]]['DailyVal{0}'.format(x)] ],axis=1)

equitytablebench['EquityCurve']=equitytablebench.sum(axis=1)





#sample
r={}                        #dictionary of returns on investment

for x in range(0,50):       #calculating n day performance in terms of returns
    r[nifty_list[x]] = ( (d[nifty_list[x]]['Close'].loc[d[nifty_list[x]].index[len(d[nifty_list[x]])-1]]) / (d[nifty_list[x]]['Open'].loc[d[nifty_list[x]].index[len(d[nifty_list[x]])-(n_days_measure_perf+1)]]) ) - 1

from operator import itemgetter

topnr = dict(sorted(r.items(), key=itemgetter(1), reverse=True)[:top_n_stocks])        #top 10 RoI stocks

d2=d        #copying into another variable to avoid confusion between daily value in benchmark and sample strategies

for x in range(0,50):                                   #date filter
    d2[nifty_list[x]] = d2[nifty_list[x]].loc[datefilter]

for x in range(0,50):                         #daily values of top n stocks                                
    if nifty_list[x] in topnr:
        d2[nifty_list[x]]['DailyVal{0}'.format(x)] = (in_eq/top_n_stocks) / (d2[nifty_list[x]]['Open'].loc[d2[nifty_list[x]].index[0]]) * (d2[nifty_list[x]]['Close'])
        
    else:
        pass

equitytablesample=pd.DataFrame()

for x in range(0,50):               #concatenating daily value columns from each top stock
    if nifty_list[x] in topnr:
        equitytablesample = pd.concat([equitytablesample, d2[nifty_list[x]]['DailyVal{0}'.format(x)] ],axis=1)
    else:
        pass

equitytablesample['EquityCurve']=equitytablesample.sum(axis=1)




#nifty
n = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/%5ENSEI?period1=1601510400&period2=1687219200&interval=1d&events=history&includeAdjustedClose=true')

n=n.loc[datefilter]         #date filter

n['DailyVal'] = in_eq / (n['Open'].loc[n.index[0]]) * n['Close']



#benchmark performance
Vbegin = equitytablebench['EquityCurve'].loc[equitytablebench['EquityCurve'].index[0]]
Vfinal = equitytablebench['EquityCurve'].loc[equitytablebench['EquityCurve'].index[len(equitytablebench.index)-1]]
t = len(equitytablebench.index) / 365

CAGRB = ( (Vfinal/Vbegin)**(1/t) - 1) * 100

dailyreturnsbench=pd.DataFrame(columns=['dailyreturnsbench'])
for x in range(0,len(equitytablebench.index)-1):
    dailyreturnsbench.loc[x+1] = ( equitytablebench['EquityCurve'].loc[equitytablebench['EquityCurve'].index[x+1]] / equitytablebench['EquityCurve'].loc[equitytablebench['EquityCurve'].index[x]] ) - 1

stddev=dailyreturnsbench.std()
mean=dailyreturnsbench.mean()

volatilityB = (stddev**(1/252)) * 100

sharpeB = (mean/stddev)**(1/252)



#sample performance
Vbegin = equitytablesample['EquityCurve'].loc[equitytablesample['EquityCurve'].index[0]]
Vfinal = equitytablesample['EquityCurve'].loc[equitytablesample['EquityCurve'].index[len(equitytablesample.index)-1]]
t = len(equitytablesample.index) / 365

CAGRS = ( (Vfinal/Vbegin)**(1/t) - 1) * 100

dailyreturnssample=pd.DataFrame(columns=['dailyreturnssample'])
for x in range(0,len(equitytablesample.index)-1):
    dailyreturnssample.loc[x+1] = ( equitytablesample['EquityCurve'].loc[equitytablesample['EquityCurve'].index[x+1]] / equitytablesample['EquityCurve'].loc[equitytablesample['EquityCurve'].index[x]] ) - 1

stddev=dailyreturnssample.std()
mean=dailyreturnssample.mean()

volatilityS = (stddev**(1/252)) * 100

sharpeS = (mean/stddev)**(1/252)



#nifty performance
Vbegin = n['DailyVal'].loc[n['DailyVal'].index[0]]
Vfinal = n['DailyVal'].loc[n['DailyVal'].index[len(n.index)-1]]
t = len(n.index) / 365

CAGRN = ( (Vfinal/Vbegin)**(1/t) - 1) * 100

dailyreturnsnifty=pd.DataFrame(columns=['dailyreturnsnifty'])
for x in range(0,len(n.index)-1):
    dailyreturnsnifty.loc[x+1] = ( n['DailyVal'].loc[n['DailyVal'].index[x+1]] / n['DailyVal'].loc[n['DailyVal'].index[x]] ) - 1

stddev=dailyreturnsnifty.std()
mean=dailyreturnsnifty.mean()

volatilityN = (stddev**(1/252)) * 100

sharpeN = (mean/stddev)**(1/252)


#PLOT
import datetime as dt

date=n['Date']
date=pd.to_datetime(date)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


fig=plt.figure(figsize=(10,6))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=90))
plt.plot_date(date,equitytablebench.EquityCurve, 'r', label='Equal Alloc Buy Hold')
plt.plot_date(date,equitytablesample.EquityCurve, 'g', label='Performance_Strat')
plt.plot_date(date,n.DailyVal, 'b', label='Nifty')
plt.legend()
plt.show()


perf={'CAGR %':[CAGRB,CAGRN,CAGRS],
    'Volatility %':[volatilityB.values,volatilityN.values,volatilityS.values],
    'Sharpe':[sharpeB.values,sharpeN.values,sharpeS.values]}
performance=pd.DataFrame(perf, index=['Equal Alloc Buy Hold','Nifty','Performance_Strat'])

#print(performance)
#fig

st.write(performance)
st.pyplot(fig)








