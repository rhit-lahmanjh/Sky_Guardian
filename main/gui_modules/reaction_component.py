import itertools
from typing import TYPE_CHECKING

from main.drone import Drone
if(TYPE_CHECKING):
    from reaction_board import ReactionInput
from flet import *

class ReactionComponent(UserControl):
    id_counter = itertools.count()

    def __init__ (self, selectedBehavior:str, selectedObject:str, drone:Drone):
        super().__init__()
        self.reaction_id = next(ReactionComponent.id_counter)
        self.title = ""
        self.behavior = selectedBehavior
        self.object = selectedObject

    def build(self):
        self.title = Text(self.behavior + " on " + self.object)

        return Container(
                    content=self.title, 
                    bgcolor = colors.INDIGO_ACCENT_200,
                    padding = 5
                    ),
        
