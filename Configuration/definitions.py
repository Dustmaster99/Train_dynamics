"""
Created on Thu Sep 25 21:27:53 2025

@author: eosjo
"""
import os
os.chdir(r'C:\Kegle_Jojo\Train_Dynamics')


from enum import Enum
from dataclasses import dataclass
from typing import List


# Time Scale seconds
STEP_SCALE = 1


@dataclass
class itinerary_data:
    path: List[str]        # lista de nomes de estações
    start_station: str
    end_station: str
    
    
@dataclass
class station_data:
    name: str
    ID: int
    time_stop: int
    enable_stop: bool
    
@dataclass
class train_data:
    name: str
    ID: int
    itinerary:str
    size: int
    init_velocity : int
    


# Dicionário de estações
STATION_TABLE = {
    "S_A": station_data(name="S_A", ID=1, time_stop= round(5/STEP_SCALE),enable_stop = True),
    "S_B": station_data(name="S_B", ID=2, time_stop= round(5/STEP_SCALE),enable_stop = True),
    "S_C": station_data(name="S_C", ID=3, time_stop= round(5/STEP_SCALE),enable_stop = True),
    "S_D": station_data(name="S_D", ID=4, time_stop= round(5/STEP_SCALE),enable_stop = True),
    "S_E": station_data(name="S_E", ID=5, time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_F": station_data(name="S_F", ID=6, time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_G": station_data(name="S_G", ID=7, time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_H": station_data(name="S_H", ID=8, time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_I": station_data(name="S_I", ID=9, time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_J": station_data(name="S_J", ID=10,time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_K": station_data(name="S_K", ID=11,time_stop= round(1/STEP_SCALE),enable_stop = True),
    "S_L": station_data(name="S_L", ID=12,time_stop= round(1/STEP_SCALE), enable_stop = True),
    "S_M": station_data(name="S_M", ID=13,time_stop= round(1/STEP_SCALE),enable_stop = True),
}

TRAIN_TABLE = {
    "T_A": train_data(name="T_A", ID=1, itinerary="I_A", size = 10, init_velocity = round(18*STEP_SCALE)),
    "T_B": train_data(name="T_B", ID=2, itinerary="I_B", size = 10, init_velocity = round(5*STEP_SCALE)),
}


# Dicionário de itinerários
ITINERARY_TABLE = {
    "I_A": itinerary_data(path=["S_A", "S_B","S_D"], start_station="S_A", end_station="S_D"),
    "I_B": itinerary_data(path=["S_D", "S_B", "S_A"], start_station="S_D", end_station="S_A"),
    "I_C": itinerary_data(path=["S_A","S_B","S_C","S_D","S_E","S_F","S_G","S_H","S_I","S_J","S_K","S_L","S_M"], start_station="S_A", end_station="S_M"),
}


# Definition of functions: 

def get_next_station_from_itinerary_table(itinerary_table, itinerary_name, current_station):
    """
    Retorna a próxima estação de um itinerário dado o nó atual.
    
    Parâmetros:
        itinerary_table (dict): dicionário de itinerários
        itinerary_name (str): chave do itinerário
        current_station (str): estação atual

    Retorna:
        str ou None: próxima estação ou None se for a última
    """
    itinerary = itinerary_table.get(itinerary_name)
    if not itinerary:
        return None  # itinerário não encontrado
    
    try:
        index = itinerary.path.index(current_station)
        # Se não for a última estação, retorna a próxima
        if index < len(itinerary.path) - 1:
            return itinerary.path[index + 1]
        else:
            return None  # já é a última estação
    except ValueError:
        return None  # estação atual não está no caminho


def get_station_info(STATION_TABLE):
    """
    Versão mais concisa usando list comprehension
    """
    station_namelist = [station_obj.name for station_obj in STATION_TABLE.values()]
    station_ids = [station_obj.ID for station_obj in STATION_TABLE.values()]
    n_stations = len(STATION_TABLE)
    time_stop = [station_obj.time_stop for station_obj in STATION_TABLE.values()]
    enable_stop = [station_obj.enable_stop for station_obj in STATION_TABLE.values()]
    return station_namelist, station_ids, n_stations, time_stop, enable_stop



def get_train_info(TRAIN_TABLE):
    """
    Versão mais concisa usando list comprehension
    """
    train_namelist = [train_obj.name for train_obj in TRAIN_TABLE.values()]
    train_ids = [train_obj.ID for train_obj in TRAIN_TABLE.values()]
    n_trains = len(TRAIN_TABLE)
    itinerary_list = [train_obj.itinerary for train_obj in TRAIN_TABLE.values()]
    size = [train_obj.size for train_obj in TRAIN_TABLE.values()]
    init_velocity  = [train_obj.init_velocity for train_obj in TRAIN_TABLE.values()]
    
    return train_namelist, train_ids, n_trains,itinerary_list, size, init_velocity
