# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 21:21:06 2025

@author: eosjo
"""

import os
os.chdir(r'C:\Kegle_Jojo\Train_Dynamics')

from enum import Enum
from dataclasses import dataclass


@dataclass
class ItinerarioInfo:
    start_name: str
    start_id: int
    end_name: str
    end_id: int


class ITINERARY (Enum):
    A = "Station A"
    B = "Station B"
    C = "Station C"
    D = "Station D"
    E = "Station E"
    
    
