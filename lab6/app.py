import flet as ft
import re
from engine import SVDEngine, Engine, PreCompSVDEngine

subject_pattern = re.compile(r"Subject: (.*)\n")
from_pattern = re.compile(r"\nFrom: (\S*)(,|\n)")
to_pattern = re.compile(r"\nTo: (\S*)(,|\n)")
date_pattern = re.compile(r"Date: (.*)\n")
body_pattren = re.compile(r"\n\n([\S\s]*)")

class Email(ft.Column):
    def __init__(self, file):
        super().__init__()
        f = open(file, errors="ignore")
        self.mail = f.read()
        f.close()
        self.mathes = {
            "date": re.search(date_pattern, self.mail),
            "subject": re.search(subject_pattern, self.mail),
            "from": re.search(from_pattern, self.mail),
            "to": re.search(to_pattern, self.mail),
            "body": re.search(body_pattren, self.mail)
        }
        def get_container_with_text(text: str):
            return ft.Container(
                ft.Text(text),
                margin=0.5,
                padding=10,
                alignment=ft.alignment.center_left,
                bgcolor=ft.Colors.CYAN_100,
                border_radius=10,
            )
        self.controls.append(get_container_with_text(f"Date: {self.mathes["date"][1]}"))
        self.controls.append(get_container_with_text("From: %s"%(self.mathes["from"][1] if self.mathes["from"][2] == "\n" else self.mathes["from"][1]+" ...")))
        if self.mathes["to"] is not None:
            self.controls.append(get_container_with_text("To: %s"%(self.mathes["to"][1] if self.mathes["to"][2] == "\n" else self.mathes["to"][1]+" ...")))
        self.controls.append(get_container_with_text(f"Subject: {self.mathes["subject"][1]}"))
        self.controls.append(get_container_with_text(self.mathes["body"][1]))


class EmailTile(ft.CupertinoListTile):
    def __init__(self, file, corelation, no):
        super().__init__()
        self.file = file
        self.data = self.file
        f = open(file, errors="ignore")
        self.mail = f.read()
        f.close()
        self.mathes = {
            "date": re.search(date_pattern, self.mail),
            "subject": re.search(subject_pattern, self.mail),
            "from": re.search(from_pattern, self.mail),
            "to": re.search(to_pattern, self.mail),
            "body": re.search(body_pattren, self.mail)
        }
        self.additional_info = ft.Text(corelation)
        self.bgcolor_activated=ft.Colors.CYAN_ACCENT_100
        self.leading = ft.Text(no)
        self.title = ft.Text(f"{self.mathes["subject"][1]}")
        froms = "From: %s"%(self.mathes["from"][1] if self.mathes["from"][2] == "\n" else self.mathes["from"][1]+" ...")
        if self.mathes["to"] is not None:
            tos = "To: %s"%(self.mathes["to"][1] if self.mathes["to"][2] == "\n" else self.mathes["to"][1]+" ...")
        else:
            tos = ""
        self.subtitle = ft.Text(f"{froms} {tos}")

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Search Engine"
    page.scroll = ft.ScrollMode.AUTO

    body = ft.Column()
    
    engine = Engine("big.npz", "terms.json", "files.json", 1)
    results = None
    email_current = None
    compression = 3

    def select_engine(e):
        nonlocal engine
        nonlocal compression
        wait.visible = True
        page.update()
        if e.data == "0":
            compression_input.visible = False
            engine = Engine("big.npz", "terms.json", "files.json", 1)
            print("basic")
        elif e.data == "1":
            compression_input.visible = False
            engine = Engine("big_normalised.npz", "terms.json", "files.json", 2)
            print("normalised")
        elif e.data == "2":
            compression_input.visible = True
            compression = int(compression_input.value)
            engine = SVDEngine("big.npz", "terms.json", "files.json", compression)
            print("svd")
        elif e.data == "3":
            compression_input.visible = False
            engine = PreCompSVDEngine("svd.npz", "terms.json", "files.json")
        print("Engine changed")
        wait.visible = False
        page.update()
    
    def search(e):
        nonlocal results
        wait.visible = True
        page.update()
        results = engine.process_query(search_bar.value, int(amount.value))
        wait.visible = False
        page.update()
        page.go("/")
        page.go("/list")
    
    def view_mail(e):
        nonlocal email_current
        email_current = e.control.data
        page.go("/mail")
    
    def back(e):
        back_button.visible = False
        page.go("/list")

    def on_route_change(event : ft.RouteChangeEvent):
        route = event.route
        nonlocal results
        nonlocal email_current
        if route == "/":
            body.controls.clear()
        elif route == "/list":
            body.controls.clear()
            l = ft.ListView()
            i = 1
            for filename, coor in results:
                tile = EmailTile(filename, coor, i)
                tile.on_click = view_mail
                l.controls.append(tile)
                i+=1
            body.controls.append(l)
        elif route == "/mail":
            back_button.visible = True
            body.controls.clear()
            body.controls.append(
                Email(email_current)
            )
        page.update()

    search_bar = ft.TextField(label="Search", width=500)
    amount = ft.TextField(label="Amount", keyboard_type=ft.KeyboardType.NUMBER, value="10", width=70)

    engine_select = ft.CupertinoSegmentedButton(
        selected_color=ft.Colors.CYAN_100,
        border_color=ft.Colors.BLACK,
        selected_index=0,
        controls=[
            ft.Container(
                    padding=ft.padding.symmetric(10, 30),
                    content=ft.Text("Basic", color=ft.Colors.BLACK),
                ),
            ft.Container(
                    padding=ft.padding.symmetric(10, 30),
                    content=ft.Text("Normalized", color=ft.Colors.BLACK),
                ),
            ft.Container(
                    padding=ft.padding.symmetric(10, 30),
                    content=ft.Text("SVD", color=ft.Colors.BLACK),
                ),
            ft.Container(
                    padding=ft.padding.symmetric(10, 30),
                    content=ft.Text("SVD-Computed", color=ft.Colors.BLACK),
                ),
        ],
        on_change=select_engine
    )

    search_button = ft.IconButton(
        ft.Icons.SEARCH,
        on_click=lambda e: search(1)
    )

    back_button = ft.IconButton(
        ft.Icons.ARROW_BACK,
        on_click=back,
        visible=False
    )

    wait = ft.Text("Wait", visible=False)

    def input_compression(e):
        nonlocal engine
        nonlocal compression
        wait.visible = True
        page.update()
        compression_input.visible = True
        compression = int(compression_input.value)
        engine = SVDEngine("big.npz", "terms.json", "files.json", compression)
        print("svd")
        print("Engine changed")
        wait.visible = False
        page.update()



    compression_input = ft.TextField(label="Compression", keyboard_type=ft.KeyboardType.NUMBER,
                                    on_submit=input_compression,
                                    value="3", visible=False, height=40, width=100)
    
    page.on_route_change = on_route_change
    
    control_bar = ft.Column(
        controls=[
            ft.Row(controls=[engine_select, compression_input, wait]),
            ft.Row(controls=[ft.Container(padding=ft.padding.only(left=5)),search_bar, amount, search_button, back_button], spacing=10)
        ]
    )

    page.add(control_bar)
    page.add(body)
    page.go("/")
    page.update()

ft.app(main)