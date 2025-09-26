"""
Created on Thu Sep 25 21:27:53 2025

@author: eosjo
"""
import os
os.chdir(r'C:\Kegle_Jojo\Train_Dynamics')


from enum import Enum
from dataclasses import dataclass
from typing import List


@dataclass
class itinerary_data:
    path: List[str]        # lista de nomes de estações
    start_station: str
    end_station: str
    
    
@dataclass
class station_data:
    name: str
    ID: int
    


# Dicionário de estações
STATION_TABLE = {
    "S_A": station_data( name = "S_A", ID = 1),
    "S_B": station_data( name = "S_B", ID = 2),
    "S_C": station_data( name = "S_C", ID = 3),
    "S_D": station_data( name = "S_D", ID = 4),

}

# Dicionário de itinerários
ITINERARY_TABLE = {
    "I_A": itinerary_data(path=["S_A", "S_B", "S_C", "S_D"], start_station="S_A", end_station="S_D"),
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
    
    return station_namelist, station_ids, n_stations





