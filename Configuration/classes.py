# -*- coding: utf-8 -*-
"""
Created on Fri Nov  7 05:42:48 2025

@author: eosjo
"""

from dataclasses import dataclass

@dataclass
class FlagState:
    previous: bool = False
    current: bool = False

    def update(self, new_value: bool):
        """Atualiza o estado, movendo o valor atual para previous."""
        self.previous = self.current
        self.current = new_value

class StateFlags:
    def __init__(self, **kwargs):
        self._states = {k: FlagState(v, v) for k, v in kwargs.items()}

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._states:
                self._states[k].update(v)
            else:
                self._states[k] = FlagState(v, v)

    def __getattr__(self, item):
        return self._states[item]