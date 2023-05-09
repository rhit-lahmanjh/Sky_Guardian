import itertools
from drone import Drone
from pickle import FALSE, TRUE
import flet as ft
from main.drone import Drone
from reaction_component import ReactionComponent
from yoloClasses import vision_class

# grabs list of possible reaction objects
object_list = [obj.name for obj in vision_class]

reaction_data = ["Flip", "Bob", "Pause", "Follow", "Run"]

# make Class that allows the user to select an object and Reaction
class ReactionInput(ft.UserControl):
    id_counter = itertools.count()

    def __init__(self, drone:Drone, name:str):
        super().__init__()
        self.name = name
        self.drone = drone
        self.board_id = next(ReactionInput.id_counter)
        self.selectedObject = ""
        self.selectedBehavior = ""
        self.badIcon = ft.Icon(name=ft.icons.QUESTION_MARK, color=ft.colors.BLUE_GREY_300, size=30)
        self.goodIcon = ft.Icon(name=ft.icons.CHECK, color=ft.colors.GREEN_300, size=30)
        self.add_reaction_button = ft.OutlinedButton(icon=ft.icons.ADD, height = 30, on_click=self.createReaction)
        self.delete_reaction_button = ft.OutlinedButton(icon=ft.icons.DELETE, height = 30, on_click=self.deleteReaction)
        self.clear_all_button = ft.OutlinedButton(icon=ft.icons.DELETE_SWEEP, height = 30, on_click=self.clear_all_reactions)

        self.reaction_list = [
        ]

        self.list_wrap = ft.Column(
            self.reaction_list,
            visable = True,
            vertical_alignment = "start",
            scroll = "auto",
            width = (self.app.page.width - 310),
            height = self.app.page.height -95
        )

        self.dd = ft.Dropdown(
                    width=300,
                    options=[],
                    label = ft.Text("Select Behavior")
        )
        
        for item in reaction_data:
            self.dd.options.append(ft.dropdown.Option(str(item)))

    def build(self):

        self.view = ft.Card( 
                content=ft.Container(
                content=ft.Column(
                [ 
                    ft.Row(
                        content = [
                            ft.Text("Reactions"), 
                            self.add_reaction_button,
                            self.delete_reaction_button,
                            self.clear_all_button
                        ],
                
                    ),
                    self.list_wrap,
                ]
                ),
                    width=400,
                    padding=10,
                )
        )
        return self.view

    def createReaction(self, e):

        def close_dig(e):
            if(hasattr(e.control, "text") and not e.control.text == "Cancel") or (type(e.control) is ft.TextField and e.control.value != ""):
                new_reaction = ReactionComponent(self, self.selectedBehavior, self.selectedObject)
            self.add_reaction(new_reaction)

            dialog.open = False
            self.page.update()
            self.update()

        def textfield_change(e):
            val = dialog.text.value

            for item in object_list:
                if val == item:
                    self.selectedObject = item
                    objectSelected = TRUE

            if dialog.text.value == "" or objectSelected == FALSE:
                create_button.disabled = TRUE
            else:
                create_button.disabled = FALSE

            self.page.update()
        dialog_text = ft.TextField(label="Input Object from COCO dataset", on_submit=close_dig, on_change=textfield_change)

        create_button = ft.ElevatedButton(text="Create", bgcolor=ft.colors.BLUE_200, on_click=close_dig, disabled=TRUE)
        dialog = ft.AlertDialog(
            title = ft.Text("Make a new reaction"),
            content=ft.Column([
                ft.Container(content = [
                    self.dd,
                    dialog_text, 
                ],
                padding = ft.padding.symmetric(horizontal=5),
                ),
            ft.Row([
                ft.ElevatedButton(
                    text="Cancel", on_click=close_dig),
                    create_button
            ],
                alignment="spaceBetween")
            ], tight=TRUE, alignment="center"
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )
        self.page.dialog = dialog
        dialog.open = TRUE
        self.page.update()
        dialog_text.focus()

    def add_reaction(self, r: ReactionComponent):
        self.reaction_list.insert(-1, list)
        self.update()

    def remove_reaction(self, r: ReactionComponent, e):
        self.reaction_list.remove(r)
        self.update()

    def clear_all_reactions(self, e):
        self.reaction_list = []
        self.update()
