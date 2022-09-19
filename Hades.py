# 仮想通貨のアービトラージを用いた自動売買Bot
#coincheck vs zaif 
#Hades3.2 では3.0の改良版0.01BTCずつ差が出た時に指値（板の一番上）で取引する。BTCを少なくすることで未決済になる確率を減らす。
#板の買値売値の差が100以上のみの取引
#trade_btcを増やす可能性あり
#zaifの注文料は（amount）0.1111X
#手数料なし
#かけコインのN倍のみの取引　
# In[1]:library
    
import ccxt
import pandas as pd
import datetime
from time import sleep
import requests

# In[2]:bitflyer

zaif = ccxt.zaif()
zaif.apiKey = '*********∆**'
zaif.secret = '***********'
exchangeA=zaif

# In[3]:coincheck

coincheck = ccxt.coincheck()
coincheck.apiKey = '***********'
coincheck.secret = '***********'
exchangeB=coincheck

# In[4]:variable

loop_times=50000
csvlist=[]
loop=0
order_signal=999
limit=0.005
N=300


# In[5]:line

url = 'https://notify-api.line.me/api/notify'
token = '***********'
headers = {'Authorization' : 'Bearer ' + token}

# In[5]:bookがbidsの量

def trade_btc(book,account_balance):
    coin=book[0][1]
    if coin>account_balance:
        coin=account_balance
    if coin>=limit:
        a=coin*1000
        a=int(a)
        coin=a/1000
    else:
        coin=0
    return coin

# In[6]:
    
print("\nこのプログラムはループ回数{0}までです。".format(loop_times))
while True:
    print(loop)
    checking_order_time=0
    
    if order_signal!=0:
        order_signal=0
        while True:
            try:
                account_balanceA=exchangeA.fetch_balance()['total']['BTC']
                account_balanceB=exchangeB.fetch_balance()['BTC']['total']
                break
            except Exception as e:
                message="{0}.".format(e)
                payload = {'message' : message}
                r = requests.post(url, headers=headers, params=payload)
                sleep(10)
    now = datetime.datetime.now()
    timeval = now.replace(microsecond=0)
    print("zaif        のBTCは{0}".format(account_balanceA))
    print("coincheck   のBTCは{0}".format(account_balanceB))
    try:
        bookA = exchangeA.fetch_order_book('BTC/JPY')
        bookB = exchangeB.fetch_order_book('BTC/JPY')
    except Exception as e:
        message="{0}.".format(e)
        payload = {'message' : message}
        r = requests.post(url, headers=headers, params=payload)
        sleep(10)
        continue
    trade_btcA=trade_btc(bookA['bids'], account_balanceA)
    trade_btcB=trade_btc(bookB['asks'], account_balanceA)
    trade_btcC=trade_btc(bookA['asks'], account_balanceB)
    trade_btcD=trade_btc(bookB['bids'], account_balanceB)
    trade_btc1=min(trade_btcA,trade_btcB)
    trade_btc2=min(trade_btcC,trade_btcD)

    
# =============================================================================
# #かけ額300倍以上の利益で取引
#     if bookB['bids'][0][0]*trade_btcA-bookA['asks'][0][0]*trade_btcA<trade_btcA*N:
#         trade_btcA=0
#     if bookA['bids'][0][0]*trade_btcB-bookB['asks'][0][0]*trade_btcB<trade_btcB*N:
#         trade_btcB=0
#     
# =============================================================================
    
    if bookA['asks'][0][0]<bookB['bids'][0][0] and trade_btc1!=0:
        try:
            result1 = exchangeA.create_order(symbol = 'BTC/JPY',type='limit',side='sell',price=bookA['asks'][0][0],amount=trade_btc1)
        except Exception as e:
            message="{0}.".format(e)
            payload = {'message' : message}
            r = requests.post(url, headers=headers, params=payload)
            sleep(10)
            continue
        else:
            try:
                result2 = exchangeB.create_order(symbol = 'BTC/JPY',type='limit',side='buy',price=bookB['bids'][0][0],amount=trade_btc1)
                order_signal=1
                message="{0}BTCをcoincheckで買い、zaifで売却しました.".format(trade_btc1)
                payload = {'message' : message}
                r = requests.post(url, headers=headers, params=payload)
            except Exception as e:
                message="stop:{0}.".format(e)
                payload = {'message' : message}
                r = requests.post(url, headers=headers, params=payload)
                sleep(10)
                break
            
    
    if bookA['bids'][0][0]>bookB['asks'][0][0] and trade_btc2!=0:
        try:
            result3 = exchangeA.create_order(symbol = 'BTC/JPY',type='limit',side='buy',price=bookA['bids'][0][0],amount=trade_btc2)
        except Exception as e:
            message="{0}.".format(e)
            payload = {'message' : message}
            r = requests.post(url, headers=headers, params=payload)
            sleep(10)
            continue
        else:
            try:
                result4 = exchangeB.create_order(symbol = 'BTC/JPY',type='limit',side='sell',price=bookB['asks'][0][0],amount=trade_btc2)
                order_signal=2
                message="{0}BTCをzaifで買い、coincheckで売却しました.".format(trade_btc2)
                payload = {'message' : message}
                r = requests.post(url, headers=headers, params=payload)
            except Exception as e:
                message="stop:{0}.".format(e)
                payload = {'message' : message}
                r = requests.post(url, headers=headers, params=payload)
                sleep(10)
                break
        
        
        
    if order_signal!=0:
        while  True:
            try:
                if exchangeB.fetch_open_orders()!=[] or exchangeA.fetch_open_orders()!=[]:
                    checking_order_time=checking_order_time+1
                    sleep(1)
                    print("checking order time = {0}".format(checking_order_time))
                else:
                    break
            except Exception as e:
                message="{0}.".format(e)
                payload = {'message' : message}
                r = requests.post(url, headers=headers, params=payload)
                sleep(10)
            
         
            
         
    if  order_signal==1:
         message="取引が完了しました。{0}円の利益です。checking order timeは{1}です。".format(bookB['bids'][0][0]*trade_btc1-bookA['asks'][0][0]*trade_btc1,checking_order_time)
         payload = {'message' : message}
         r = requests.post(url, headers=headers, params=payload)  
         csvlist.append([timeval,
                         result1,result2,
                         bookB['bids'][0][0]*trade_btcA-bookA['asks'][0][0]*trade_btcA,
                         checking_order_time])
         df=pd.DataFrame(csvlist,columns=['time','result','result','profit','tradetime'])
         df.to_csv("'***********'".format(datetime.date.today(),now.hour), index=False)
         sleep(1)
         
    if  order_signal==2:
         message="取引が完了しました。{0}円の利益です。checking order timeは{1}です。".format(bookA['bids'][0][0]*trade_btc2-bookB['asks'][0][0]*trade_btc2,checking_order_time)
         payload = {'message' : message}
         r = requests.post(url, headers=headers, params=payload)  
         csvlist.append([timeval,
                         result3,result4,
                         bookA['bids'][0][0]*trade_btcB-bookB['asks'][0][0]*trade_btcB,
                         checking_order_time])
         df=pd.DataFrame(csvlist,columns=['time','result','result','profit','tradetime'])
         df.to_csv("'***********'".format(datetime.date.today(),now.hour), index=False)
         sleep(1)
         
         
         
    loop=loop+1
    
    if loop==loop_times:
        break
    sleep(1)
    
    
    
    
    
    
    
    