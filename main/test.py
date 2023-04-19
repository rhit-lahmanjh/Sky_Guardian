import flet as ft
from flet import *
from getkey import getkey, key

def main(page:Page):

	# opening the file in read mode
    my_file = open("main/coco_class_labels.txt", "r")

    # reading the file
    data_read = my_file.read()

    # replacing end splitting the text 
    # when newline ('\n') is seen.
    data = data_read.split("\n")
    print(data)
    print(type(data))
    my_file.close()

    reaction_data = ["flipOnBanana", "bobOnScissors", "pauseOnSoccerBall", "followCellPhone", "RunFromBanana"]

    class ReactionInput(ft.UserControl):
        def build(self):
            self.resultdata = ListView()
            self.resultlist = resultlist =  ft.Card(
                content=ft.Container(
                    width=500,
                    content=ft.Column([],spacing=0),
                    padding=ft.padding.symmetric(vertical=10),
                    )
            )
            self.resultcon = Container(
                bgcolor="red200",
                padding=10,
                margin=10,
                offset=transform.Offset(-2,0),
                animate_offset = animation.Animation(600,curve="easeIn"),
                content=Column([resultdata])
            )
            self.t1 = ft.Text()
            self.t2 = ft.Text()
            
            self.b = ft.ElevatedButton(text="Submit", on_click=button_clicked)
            self.dd = ft.Dropdown(
                width=300,
                options=[]
            )
            
            for item in reaction_data:
                self.dd.options.append(ft.dropdown.Option(str(item)))
                
            # HIDE RESULT FOR YOU SEARCH DEFAULT
            self.resultcon.visible = False

            self.txtsearch = TextField(label="Input object from COCO dataset",on_change=searchnow, on_submit=getresult)
            
            return ft.Card( 
                    content=ft.Container(
                    content=ft.Column(
                    [
                        Text("Drone 1 Reaction:",size=30,weight="bold"),
                        self.txtsearch,
                        self.resultcon,
                        ft.Column([
                            self.dd, self.b
                        ])
                    ]
                    ),
                    width=400,
                    padding=10,
                    )
        )
        
        def getresult(self, e):
            self.resultcon.offset = transform.Offset(-2,0)
            self.resultdata.controls.clear()
            page.update()
                
            self.mysearch = e.control.value
            self.result = []

            # IF NOT BLANK YOU TEXTFIELD SEARCH THE RUN FUNCTION
            if not self.mysearch == "":
                for item in data:
                    if self.mysearch in item:
                        self.result.append(item)
            
            self.t1.value = f"Object selected: {self.result[0]}"
            
        def searchnow(self,e):
            self.mysearch = e.control.value
            result = []

            # IF NOT BLANK YOU TEXTFIELD SEARCH THE RUN FUNCTION
            if not self.mysearch == "":
                self.resultcon.visible = True
                for item in data:
                    if self.mysearch in item:
                        self.resultcon.offset = transform.Offset(0,0)
                        result.append(item)
                page.update()

            # IF RESULT THERE DATA THEN PUSH DATA TO WIDGET CONTAINER Resultcon
            if result:
                self.resultdata.controls.clear()
                print(f"Your result {result}")
                for x in result[:3]:
                    self.resultdata.controls.append(
                    Text(x, size=20,color="white")
                        )
                page.update()
                
            else:
                self.resultcon.offset = transform.Offset(-2,0)
                self.resultdata.controls.clear()
                page.update()
                
        def button_clicked(self, e):
            self.t2.value = f"Reaction selected: {dd.value}"
            page.update()
                # self.text = ft.Text(str(self.counter))
                # return ft.Row([self.text, ft.ElevatedButton("Add", on_click=self.add_click)])
        
    
    resultdata = ListView()

    resultlist =  ft.Card(
            content=ft.Container(
                width=500,
                content=ft.Column([],spacing=0),
                padding=ft.padding.symmetric(vertical=10),
            )
        )
    
    ft.ListTile( title=ft.Text("One-line list tile"),)
    
    resultcon = Container(
        bgcolor="red200",
        padding=10,
        margin=10,
        offset=transform.Offset(-2,0),
        animate_offset = animation.Animation(600,curve="easeIn"),
        content=Column([resultdata])
        )

    def getresult(e):
        resultcon.offset = transform.Offset(-2,0)
        resultdata.controls.clear()
        page.update()
            
        mysearch = e.control.value
        result = []

        # IF NOT BLANK YOU TEXTFIELD SEARCH THE RUN FUNCTION
        if not mysearch == "":
            for item in data:
                if mysearch in item:
                    result.append(item)
        
        t1.value = f"Object selected: {result[0]}"
        
    
    def searchnow(e):
        mysearch = e.control.value
        result = []

        # IF NOT BLANK YOU TEXTFIELD SEARCH THE RUN FUNCTION
        if not mysearch == "":
            resultcon.visible = True
            for item in data:
                if mysearch in item:
                    resultcon.offset = transform.Offset(0,0)
                    result.append(item)
            page.update()

        # IF RESULT THERE DATA THEN PUSH DATA TO WIDGET CONTAINER Resultcon
        if result:
            resultdata.controls.clear()
            print(f"Your result {result}")
            for x in result[:3]:
                resultdata.controls.append(
                   Text(x, size=20,color="white")
					)
            page.update()
        else:
            resultcon.offset = transform.Offset(-2,0)
            resultdata.controls.clear()
            page.update()

    def button_clicked(e):
        t2.value = f"Reaction selected: {dd.value}"
        page.add(t1, t2)
        page.update()

    t1 = ft.Text()
    t2 = ft.Text()

    b = ft.ElevatedButton(text="Submit", on_click=button_clicked)
    dd = ft.Dropdown(
        width=300,
        options=[]
    )
    for item in reaction_data:
        dd.options.append(ft.dropdown.Option(str(item)))
            
    # HIDE RESULT FOR YOU SEARCH DEFAULT
    resultcon.visible = False

    txtsearch = TextField(label="Input object from COCO dataset",on_change=searchnow, on_submit=getresult)

    card1 = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        Text("Drone 1 Reaction:",size=30,weight="bold"),
                        txtsearch,
                        resultcon,
                        ft.Column([
                            dd, b
                        ])
                    ]
                ),
                width=400,
                padding=10,
            )
        )
    
    card2 = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        Text("Drone 2 Reaction:",size=30,weight="bold"),
                        txtsearch,
                        resultcon,
                        ft.Column([
                            dd, b
                        ])
                    ]
                ),
                width=400,
                padding=10,
            )
        )
    
    page.add(ReactionInput(), ReactionInput())

ft.app(target=main)