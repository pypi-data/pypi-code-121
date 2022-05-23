#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 14:04:07 2022

@author: yuefanji
"""

import math
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider


def cycling_CCCV(file_name,cycle_num):
    '''
    This function helps the user plot the battery cycling data for the visualization

    Parameters
    ----------
  
    file_name : str
        file name of the file to be read. Should be the battery cycling data.
    cycle_num : in
        battery cycle number.

    Returns
    -------
    fig : figure
        Plot of charge discharge curve.
    '''
 
    
    
    df=pd.read_csv(file_name)
    charge=cycling_data_processing(df,cycle_num,'charge');
    discharge=cycling_data_processing(df,cycle_num,'discharge');
    
    plt.plot(charge['Capacity(Ah)'],charge['Voltage(V)'],label='charge')
    plt.plot(discharge['Capacity(Ah)'],discharge['Voltage(V)'],label='discharge')
    plt.legend()
    plt.xlabel('Capacity(Ah)')
    plt.ylabel('Voltage(V)')
    fig = plt.gcf()
    return(fig)

def diff_cap(file_name,cycle_num):
    '''
    

     This function helps the user plot the differential capacity data for the visualization

     Parameters
     ----------
     file_name : str
         file name of the file to be read. Should be the battery cycling data.
     cycle_num : in
         battery cycle number.

     Returns
     -------
     fig : figure
        Plot of differential capacity curve.
     '''
     
    df=pd.read_csv(file_name)
    charge=cycling_data_processing(df,cycle_num,'charge')
    discharge=cycling_data_processing(df,cycle_num,'discharge')
    charge_V=charge['Voltage(V)'][(charge['Voltage(V)']<4.18)]
    charge_cap=charge['Capacity(Ah)'][(charge['Voltage(V)']<4.18)]
    discharge_V=discharge['Voltage(V)'][(discharge['Voltage(V)']<4.18)]
    discharge_cap=discharge['Capacity(Ah)'][(discharge['Voltage(V)']<4.18)]
    
    dqdv_charge=np.diff(charge_cap)/np.diff(charge_V)

    N_charge=len(dqdv_charge)
    dqdv_discharge=np.diff(discharge_cap)/np.diff(discharge_V)
    N_discharge=len(dqdv_discharge)
    plt.plot(charge_V[0:N_charge],dqdv_charge,label='charge')
    plt.plot(discharge_V[0:N_discharge],dqdv_discharge,label='discharge')
    plt.legend()
    plt.xlabel('Voltage(V)')
    plt.ylabel('dQ/dV')
    fig = plt.gcf()
    return (fig)

def cycling_data_processing(df,cycle_num,data_type):
    '''
    
    This function helps user to process the battery cycling data
    
    Parameters
    ----------
    df : DataFrame
        dataframe of the battery cycling data.
    cycle_num : int
        cycle number of interest.
    data_type : str
        input 'charge' for the charge data
        input 'discharge' for the discharge data .

    Returns
    -------
    A : DataFrame
        dataframe of the battery cycling data for the cycle number of interest.

    '''
    
    if data_type == 'discharge':
        A=df[(df['Cyc#']==cycle_num)&(df['Current(A)']<0)]
    if data_type == 'charge':
        A=df[(df['Cyc#']==cycle_num)&(df['Current(A)']>0)]
        
    return (A)

def Capacity_voltage_extract(df):
    '''
    

    Parameters
    ----------
    df : DataFrame
        dataframe of the pre processed battery cycling data.

    Returns
    -------
    dataframe with column 'Capacity(Ah)' and 'Voltage(V)'.

    '''
    df_1=pd.DataFrame()
    df_1['Capacity(Ah)']=df['Capacity(Ah)']
    df_1['Voltage(V)']=df['Voltage(V)']
    return(df_1)
    

def impedance_data_processing(text_file):
    '''
    

    Parameters
    ----------
    text_file : str
        file name of the impedance data.

    Returns
    -------
    the dataframe with column 'Z1', 'Z2', and 'frequency'.

    '''
    data=np.loadtxt(text_file,delimiter=",",skiprows=11)
    f=data[:,0]
    Z1=data[:,4]
    Z2=data[:,5]
    df=pd.DataFrame()
    df1=pd.DataFrame()
    df['frequency']=f
    df['Z1']=Z1
    df['Z2']=Z2
    df1=df.copy()
    df1=df1[(df1['Z2']<0)]
    df1.reset_index(inplace = True)
    return(df1)

def Nyquist_plot_UI(text_file):
    '''
    
    Parameters
    ----------
    text_file : str
        file name of the impedance data .
    Returns
    -------
    Nyquist_plot for the visualization.
    '''
    df=impedance_data_processing(text_file)
    return(Nyquist_plot(df))
    
def Nyquist_plot(df):
    '''
    

    Parameters
    ----------
    df : DataFrame
        dataframe that is processed by impedance_data_processing() .

    Returns
    -------
    fig : figure
        Nyquist_plot for the visualization.

    '''
    
    plt.plot(df['Z1'],-df['Z2'])
    plt.xlabel('Z1')
    plt.ylabel('-Z1')
    fig = plt.gcf()
    return (fig)
    
def dis_cap(df,max_cycle):
    '''
    
    Parameters
    ----------
    df : DataFrame
        dataframe of battery cycling data.
    max_cycle : in
        maximum cycle of interest.

    Returns
    -------
    capacity at the max_cycle

    '''
    N=max_cycle+1
    cap=np.zeros(N)
    for i in range(0,N):
        discharge=cycling_data_processing(df,i,'discharge')

        cap[i]=discharge['Capacity(Ah)'].iloc[-1]

    return(cap[-1])

def cap_ret(df,max_cycle):
    '''
    
    Parameters
    ----------
    df : DataFrame
        dataframe of battery cycling data.
    max_cycle : int
        maximum cycle of interest.

    Returns
    -------
    Capacity retention for all cycles up to the max_cycle

    '''
    N=max_cycle+1
    ret=np.zeros(max_cycle)
    discharge=cycling_data_processing(df,1,'discharge')
    first_cap=discharge['Capacity(Ah)'].iloc[-1]
    ret[0]=1
    for i in range(2,N):
        discharge=cycling_data_processing(df,i,'discharge')
        ret[i-1]=(discharge['Capacity(Ah)'].iloc[-1])/first_cap

    return(ret*100)

def dynamic_cycling(file_name):
    BT=pd.read_csv(file_name)
    N=BT['Cyc#'].max()
    
    fig, ax = plt.subplots()
    vpd, = ax.plot([], [], lw=2)
    vpc, = ax.plot([], [], lw=2)   
    cycle1 = fig.text(0.95,0.9,'',ha='right', va='top', fontsize=24)
    colors = plt.get_cmap('hsv', N)  
    def animate(i):
        discharge=cycling_data_processing(BT,i,'discharge')
        dcap=discharge['Capacity(Ah)']
        
        dV=discharge['Voltage(V)']
        
        
        charge=cycling_data_processing(BT,i,'charge')
        ccap=charge['Capacity(Ah)']
        
        cV=charge['Voltage(V)']
        
        
        vpd.set_data(dcap.to_numpy(), dV.to_numpy())
        vpd.set_color(colors(i))
        vpc.set_data(ccap.to_numpy(), cV.to_numpy())
        vpc.set_color(colors(i))
        cycle1.set_text('Cycle'+str(i))
        cycle1.set_color(colors(i))        
        
    anim = FuncAnimation(fig, animate, frames=np.arange(1,N,1), interval=50, repeat=True)    
    plt.show()
    plt.xlabel('Capacity, [Ah]')
    plt.ylabel('Voltage, [V]')
    plt.xlim([-0.1,1.5])
    plt.ylim([2.4,4.3])
    fig.tight_layout()
    return anim


def dynamic_dqdv(file_name):
    BT=pd.read_csv(file_name)   
    N=BT['Cyc#'].max()   
    fig1, ax1 = plt.subplots()
    dqdvc, = ax1.plot([], [], lw=2)
    dqdvd, = ax1.plot([], [], lw=2)   
    cycle2 = fig1.text(0.85,0.85,'',ha='right', va='top', fontsize=24)
    colors = plt.get_cmap('coolwarm', N)
    
    def animate_1(i):
                 
        charge=cycling_data_processing(BT,i,'charge')
        discharge=cycling_data_processing(BT,i,'discharge')
        charge_V=charge['Voltage(V)'][(charge['Voltage(V)']<4.18)]
        charge_cap=charge['Capacity(Ah)'][(charge['Voltage(V)']<4.18)]
        discharge_V=discharge['Voltage(V)'][(discharge['Voltage(V)']<4.18)]
        discharge_cap=discharge['Capacity(Ah)'][(discharge['Voltage(V)']<4.18)]
        
        dqdv_charge=np.diff(charge_cap)/np.diff(charge_V)
        
        N_charge=len(dqdv_charge)
        dqdv_discharge=np.diff(discharge_cap)/np.diff(discharge_V)
        N_discharge=len(dqdv_discharge)
        # plt.plot(charge_V[0:N_charge],dqdv_charge,label='charge')
        # plt.plot(discharge_V[0:N_discharge],dqdv_discharge,label='discharge')
         
        
        dqdvc.set_data(charge_V[0:N_charge], dqdv_charge)
        dqdvc.set_color(colors(i))
        dqdvd.set_data(discharge_V[0:N_discharge], dqdv_discharge)
        dqdvd.set_color(colors(i))
        cycle2.set_text('Cycle'+str(i))
        cycle2.set_color(colors(i))
        # miny=min(min(dqdv_charge),min(dqdv_discharge))
        # maxy=max(max(dqdv_charge),max(dqdv_discharge))
        # ax1.set_ylim(round(miny),round(maxy))
        # ax1.set_ylim(-10, 10)
        
    anim = FuncAnimation(fig1, animate_1, frames=np.arange(1,N,1), interval=30, repeat=True)
    
    plt.show()
    plt.ylabel('dQdV, [Ah/V]')
    plt.xlabel('Voltage, [V]')
    plt.xlim([2.4,4.2])
    plt.ylim([-3,3])
    fig1.tight_layout()
    return anim
def interactive_cycling(file_name):
    
    BT=pd.read_csv(file_name)

    N=BT['Cyc#'].max()
    
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.2, top=0.75)
    
    ax_cycle = fig.add_axes([0.3, 0.85, 0.4, 0.05])
    ax_cycle.spines['top'].set_visible(True)
    ax_cycle.spines['right'].set_visible(True)
    
    
    
    s_cycle = Slider(ax=ax_cycle, label='Cycle Number', valmin=1, valmax=N-1,
                  valinit=1,valfmt='Cycle %i', facecolor='#cc7000')
    
    cyc_num=1
    discharge=cycling_data_processing(BT,cyc_num,'discharge')
    dcap=discharge['Capacity(Ah)']
    
    dV=discharge['Voltage(V)']
    
    
    charge=cycling_data_processing(BT,cyc_num,'charge')
    ccap=charge['Capacity(Ah)']
    
    cV=charge['Voltage(V)']
    
    vpd, = ax.plot(dcap.to_numpy(), dV.to_numpy(), lw=2)
    vpc, = ax.plot(ccap.to_numpy(), cV.to_numpy(), lw=2)
    
    ax.set_xlabel('Capacity, [Ah]')
    ax.set_ylabel('Voltage, [V]')
    ax.set_xlim([-0.1,1.5])
    ax.set_ylim([2.4,4.3])
    
    def update(val):
        cyc_num = int(s_cycle.val)

        discharge=cycling_data_processing(BT,cyc_num,'discharge')
        
        dcap=discharge['Capacity(Ah)']
        
        dV=discharge['Voltage(V)']
        
        
        charge=cycling_data_processing(BT,cyc_num,'charge')
        ccap=charge['Capacity(Ah)']
        
        cV=charge['Voltage(V)']
        
        
        vpd.set_data(dcap.to_numpy(), dV.to_numpy())
        
        vpc.set_data(ccap.to_numpy(), cV.to_numpy())
        
        fig.canvas.draw_idle()
    
    s_cycle.on_changed(update)
    plt.show()
    return()



def interactive_dqdv(file_name):
    
    BT=pd.read_csv(file_name)

    N=BT['Cyc#'].max()
    
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.2, top=0.75)
    
    ax_dqdv = fig.add_axes([0.3, 0.85, 0.4, 0.05])
    ax_dqdv.spines['top'].set_visible(True)
    ax_dqdv.spines['right'].set_visible(True)
    
    
    
    s_dqdv = Slider(ax=ax_dqdv, label='Cycle Number', valmin=1, valmax=N-1,
                  valinit=1,valfmt='Cycle %i', facecolor='#cc7000')
    
    cyc_num=1
    

    charge=cycling_data_processing(BT,cyc_num,'charge')
    discharge=cycling_data_processing(BT,cyc_num,'discharge')
    charge_V=charge['Voltage(V)'][(charge['Voltage(V)']<4.18)]
    charge_cap=charge['Capacity(Ah)'][(charge['Voltage(V)']<4.18)]
    discharge_V=discharge['Voltage(V)'][(discharge['Voltage(V)']<4.18)]
    discharge_cap=discharge['Capacity(Ah)'][(discharge['Voltage(V)']<4.18)]
    
    dqdv_charge=np.diff(charge_cap)/np.diff(charge_V)
    
    N_charge=len(dqdv_charge)
    dqdv_discharge=np.diff(discharge_cap)/np.diff(discharge_V)
    N_discharge=len(dqdv_discharge)
    
    dqdvc,= ax.plot(charge_V[0:N_charge], dqdv_charge)
    dqdvd,= ax.plot(discharge_V[0:N_discharge], dqdv_discharge)
    ax.set_xlabel('Voltage, [V]')
    ax.set_ylabel('dQ/dV, [Ah/V]')

    def update(val):
        cyc_num = int(s_dqdv.val)
        charge=cycling_data_processing(BT,cyc_num,'charge')
        discharge=cycling_data_processing(BT,cyc_num,'discharge')
        charge_V=charge['Voltage(V)'][(charge['Voltage(V)']<4.18)]
        charge_cap=charge['Capacity(Ah)'][(charge['Voltage(V)']<4.18)]
        discharge_V=discharge['Voltage(V)'][(discharge['Voltage(V)']<4.18)]
        discharge_cap=discharge['Capacity(Ah)'][(discharge['Voltage(V)']<4.18)]
        
        dqdv_charge=np.diff(charge_cap)/np.diff(charge_V)
        
        N_charge=len(dqdv_charge)
        dqdv_discharge=np.diff(discharge_cap)/np.diff(discharge_V)
        N_discharge=len(dqdv_discharge)
        
        
        dqdvc.set_data(charge_V[0:N_charge], dqdv_charge)
        dqdvd.set_data(discharge_V[0:N_discharge], dqdv_discharge)
        fig.canvas.draw_idle()
    
    s_dqdv.on_changed(update)
    plt.show()
    return()


    
