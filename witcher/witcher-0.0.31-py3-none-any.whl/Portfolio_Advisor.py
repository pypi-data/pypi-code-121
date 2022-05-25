############################################
#### Date   : 2022-03-25              ######
#### Author : Babak Emami             ######
#### Model  : Stock Advisor           ######
############################################

###### import requirments ##################


import pickle
import witcher
from IPython.display import display, HTML

MC_URL="https://github.com/BabakEA/witcher/raw/master/Modern_portfolio/Witcher_MC_0.3.pkl"

        



############################################

def model_Generator():
    #Model_location=witcher.__file__.replace("__init__.py","util\\Witcher_MC_0.3.pkl")
    Model_location=witcher.__file__.replace("__init__.py","util\\Witcher_MC_0.3.pkl")
    if os.path.exists(Model_location):
        #print('Loading the Modern portfolio Optimizer powered by Witcher ....')
        print('Loading the Modern portfolio Optimizer powered by Witcher ....')
        
        MC = pickle.load(open(Model_location, 'rb'))
        return MC
    else:
        #print("training a New Model")
        print("Loading API ....")
        resp= requests.get(MC_URL, allow_redirects=True)
        MC=pickle.loads(resp.content)
        
    return MC

###########################################
MC_MODEL=model_Generator()
exec(pickle.loads(MC_MODEL)) 
###########################################
#class Modern_portfolio_optimizer(Portfolio_Analysis):

        
class Witcher_Portfolio():
    
    
    display(HTML("<style>div.output_scroll { height: 44em; }</style>"))
    
    def __init__(self):
        self._indicator =["Open" ,"High","Low","Close" ,"Adj Close"]
        
        self._BTN_select = widgets.Button(description='Analysis')
        self._BTN_outt = widgets.Output()
        self._Plot_dict={}
        _ = widgets.interact(self._Chooser)
    
    def _Chooser(self):
        #Hbox_Comment=[HBox (Labe(Descripttion="Months to recover form the begining ....."))]
        #print("""just started""")
        HBOX_COMMENT=HBox([Label('Please select your stock list and date preiod to analyze ...')])
        self._Selected_indicator = widgets.Dropdown(
                        #options=list(self.DICT[Sector].keys()),
                        options=self._indicator,
                        value="Adj Close",
                        description='Stock value:',
                        disabled=False)
        
        self._Start_date=widgets.DatePicker(
            value=date.today()-timedelta(days=720),
            description='Start Date',
            disabled=False
        )
        self._End_date=widgets.DatePicker(
            value=date.today(),
            description='End Date',
            disabled=False
        )
        
        self._Stock_list=widgets.Textarea(
        value="""AAPL,COST,GO,SPY,SPOT""",
        placeholder='Stock List',
        description='Stock_list:',
        rows=2,  
        layout=widgets.Layout(width="50%",height="Auto"))
        
        #### return the selected values 
        self._BTN_select.on_click(self.on_button_clicked) #Function to run on click

        container2 = widgets.VBox([HBOX_COMMENT,self._Selected_indicator,
                                   self._Start_date,self._End_date,
                                   self._Stock_list,self._BTN_select,self._BTN_outt])
        display(container2)
    ################################################################################
    def on_button_clicked(self,_):
        with self._BTN_outt:
            #clear_output()
            #print('Button clicked')
            self._BTN_outt.clear_output()
            widgets.Output().clear_output()
            portfolio=self._Stock_list.value.strip()
            if "list" in str(type(portfolio)):
                portfolio=[re.sub("[","'",'"',"]","",x).upper() for x in portfolio]
            else:
                portfolio="".join(portfolio)
                portfolio=[x.replace(" ","").upper() for x in portfolio.split(",")] 
            
            End_date=str(self._End_date.value)
            Start_date=str(self._Start_date.value)
            close=self._Selected_indicator.value
            

            print(portfolio)
            #portfolio=['COST', 'WMT', 'TGT', 'DG']
            self.report=Portfolio_Analysis(portfolio=portfolio,
                                  close=str(close),
                                  BASE="spy",start=Start_date,end=End_date)

            
            
            
            self.Dataset=self.report.Dataset

            Selected_Stock = widgets.Output()
            Portfolio_vs_Market = widgets.Output()
            Possible_Profit=widgets.Output()
            Modern_portfolio=widgets.Output()
            

            tab = widgets.Tab(children = [Selected_Stock, Portfolio_vs_Market,Possible_Profit,Modern_portfolio])
            tab.set_title(0, 'Selected_Stock')
            tab.set_title(1, 'Portfolio_vs_Market')
            tab.set_title(2, 'Possible_Profit')
            tab.set_title(3, 'Modern_portfolio')
            display(tab)

            with Selected_Stock:

                try:
                    self.report.PortFolio_Report["PLOT"]["Selected_Stock"]()
                except:
                    pass

            with Portfolio_vs_Market:
                    self.report.PortFolio_Report["PLOT"]["Portfolio_vs_Market"]()

                
            with Possible_Profit:
                self.report.PortFolio_Report["PLOT"]["Absolute"]()
                self.report.PortFolio_Report["PLOT"]["Percentage"]()
            with Modern_portfolio:
                try:
                    self.report.PortFolio_Report["PLOT"]["MC"]()
                except:
                    self.report.PortFolio_Report["PLOT"]["_MC"]()
                    

    
    
###################################################################################
#### sample:
#### PortFolio_list=['COST', 'WMT', 'TGT', 'DG']
#### report = witcher.Stock_Market_Advisor.Modern_Portfolio_Optimizer( portfolio=PortFolio_list,
#### close="Adj Close",BASE="spy",start="2010-01-01",end="Today")
#### help(report)
###################################################################################

###################################################################################


###################################################################################



        
    
    
    
    
