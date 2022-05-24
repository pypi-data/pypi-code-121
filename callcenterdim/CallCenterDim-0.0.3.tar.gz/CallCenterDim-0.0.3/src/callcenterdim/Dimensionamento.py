
import math as mt


def ProbCallWaits(Calls,Reporting_Period,average_handling_time,agents):
    Intensity = (Calls / (Reporting_Period * 60)) * average_handling_time
    Occupancy = Intensity / agents
    A_n = 1
    SumA_k = 0
    
    count = agents
    
    while(count != 0):
        A_k = A_n * count / Intensity
        SumA_k = SumA_k + A_k
        A_n = A_k
        count = count-1
    
    prob = 1 / (1 + ((1 - Occupancy) * SumA_k))
    return prob


def ServiceLevel(Calls,Reporting_Period,average_handling_time, service_level_time,agents):
    Intensity = (Calls / (Reporting_Period * 60)) * average_handling_time
    ResultServiceLevel = 1 - (ProbCallWaits(Calls, Reporting_Period, average_handling_time, agents) * mt.exp(-(agents - Intensity) * service_level_time / average_handling_time))
    return ResultServiceLevel 



def AgentsReq(Calls,Reporting_Period,average_handling_time,service_level_percent,service_level_time):
    
    Intensity = (Calls / (Reporting_Period * 60)) * average_handling_time
    minagents = round(Intensity)
    agents = minagents
    
    while(ServiceLevel(Calls, Reporting_Period, average_handling_time, service_level_time, agents)< service_level_percent):
        agents = agents + 1
    Result = agents
    return Result

def AgentsFTE(Calls,Reporting_Period,average_handling_time,service_level_percent,service_level_time,Shrinkage):

    Intensity = (Calls / (Reporting_Period * 60)) * average_handling_time
    minagents = round(Intensity)
    if(minagents < 1):
        minagents = 1
    
    agents = minagents

    while(ServiceLevel(Calls, Reporting_Period, average_handling_time, service_level_time, agents) < service_level_percent):
        agents = agents + 1
    ResultAgentsFTE = round(agents / (1 - Shrinkage))
    return ResultAgentsFTE
