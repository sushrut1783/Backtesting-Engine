import os
import csv
import numpy as np
import pandas as pd
from Bardata import BarData


# class Strategy():
#     def __init__():
#         return

def Dates(start_date : str, end_date : str):
    date = []
    return date


class Engine():
    def __init__(self, path,):
        self.index_data = None
        self.path = path
        self.data = None
        self.Bar_Data = None
        self.curr_bar : list[BarData] = []
        self.strategy_config = None
        self.traded_file_path = None
        self.traded_orders = {}
        self.requested_orders = []
        self.total_pnl = None
        return

    def DataLoader(self):
        try:
            self.index_data = pd.read_csv(self.path)
        except FileNotFoundError:
            print(f"Error: The file at {self.path} was not found.")
        except pd.errors.EmptyDataError:
            print("Error: The file is empty.")
        except pd.errors.ParserError:
            print("Error: The file could not be parsed.")
        return 

    def Current_Bar(self):
        if self.index_data is None:
            self.DataLoader()

        # only for testing purpose, should be commented out later
        # self.BarUpdate()
        ###################


        self.Bar_Data = self.index_data.loc[(self.index_data['log_time']==self.data['timestamp'])&(self.index_data['symbol']==self.data['stock'][0])&(self.index_data['contract_name'].str.split('_').str[2].isin(self.data['exp_code']))]
        for _, bar in self.Bar_Data.iterrows():
            curr = BarData(**bar.to_dict())
            self.curr_bar.append(curr)
        # self.checkAllCondition()
        return


    def longCondition(self):
        # self.tradeExecution('NSE_BANKNIFTY_100_C_4640000',1)
        return

    def ShortCondition(self):
        # self.tradeExecution('NSE_BANKNIFTY_100_C_4640000',1)
        return

    def exit(self):
        return
    
    def calculatePnl(self,contract,trade_price,quantity):


        if trade_price is None:
            contract_bar_close_px = self.Bar_Data.loc[self.Bar_Data['contract_name']==contract,'close']
            if not contract_bar_close_px.empty :
                trade_price = contract_bar_close_px.iloc[0]
            else :
                trade_price = np.nan
                return
            
        if np.isnan(trade_price):
            return
        
        
        pnl = self.traded_orders[contract]['pnl'] + (trade_price - self.traded_orders[contract]['trade_price'])*(self.traded_orders[contract]['quantity'])
        new_quantity = quantity + self.traded_orders[contract]['quantity']
        self.traded_orders[contract]['trade_price']=trade_price
        self.traded_orders[contract]['quantity'] = new_quantity
        self.traded_orders[contract]['timestamp'] = self.data['timestamp']
        self.traded_orders[contract]['pnl'] = pnl
        # print(self.traded_orders[contract]['trade_price'],self.traded_orders[contract]['quantity'],self.traded_orders[contract]['pnl'])
        return


    def tradeExecution(self,contract,quantity):
        # self.Bar_Data = self.Current_Bar()
        contract_bar_close_px = self.Bar_Data.loc[self.Bar_Data['contract_name']==contract,'close']
        if not contract_bar_close_px.empty :
            Trade_price = contract_bar_close_px.iloc[0]
        else :
            Trade_price=None

        self.traded_orders.setdefault(contract,{'timestamp' : self.data['timestamp'],'quantity' : 0,'trade_price' : 0,'pnl' : 0})
        # print(self.traded_orders[contract])
        self.calculatePnl(contract=contract,trade_price=Trade_price,quantity=quantity)

        order = [
            [self.traded_orders[contract]['timestamp'],contract,self.traded_orders[contract]['trade_price'],self.traded_orders[contract]['quantity'],self.traded_orders[contract]['pnl']],
        ]

        self.requested_orders.append([self.data['timestamp'],contract,quantity,Trade_price])
        
        with open(self.traded_file_path,'a',newline='') as file:
            writer = csv.writer(file)
            writer.writerows(order)
        return

    def BarUpdate(self,curr_time : str):
    # def BarUpdate(self):
        self.data={
            'stock' : self.strategy_config['stock'],
            'exp_code' : self.strategy_config['exp_code'],
            'timestamp' : curr_time,
            'Date' : curr_time[:10],
        }
        return

    def Backtesting(self,start_date,end_date, config : dict):
        self.strategy_config = config
        start = start_date + ' 0915'
        end = end_date + ' 0916'

        directory = os.getcwd()
        file = start_date+'_Traded_orders.csv'
        req_order_file = start_date+'_Requested_orders.csv'

        os.makedirs(directory,exist_ok=True)
        if self.traded_file_path is None:
            self.traded_file_path = os.path.join(directory,file)

        req_order_file = os.path.join(directory,req_order_file)

        header = [["timestamp","contract","trade_price","quantity","pnl"],]
        with open(self.traded_file_path,'w',newline='') as file:
            writer = csv.writer(file)
            writer.writerows(header)

        times = pd.date_range(start=start, end=end, freq='s')
        for time in times:
            curr_time = str(time).replace(":","")
            curr_time = curr_time+'.000000000'
            self.data=None
            self.BarUpdate(curr_time=curr_time)
            self.Current_Bar()

        with open(req_order_file,'w',newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.requested_orders)

        if self.total_pnl is None:
            self.total_pnl = 0
        
        for contracts in self.traded_orders:
            if self.traded_orders[contracts]['quantity'] == 0:
                self.total_pnl = self.total_pnl + self.traded_orders[contracts]['pnl']
            else:
                # self.calculatePnl(contracts,None,self.traded_orders[contracts]['quantity'])
                self.tradeExecution(contract=contracts,quantity= -self.traded_orders[contracts]['quantity'])
                self.total_pnl = self.total_pnl + self.traded_orders[contracts]['pnl']
        
        print("Total Pnl of the strategy is ",self.total_pnl)
        
        return 
        

    def StrategyStats(self):
        return


