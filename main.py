import os
import random
import time

from RPY_manager import RPY_manager
import flet as ft
from renpy_tool import *


def main(page: ft.Page):
    running_log("启动 RPY_manager")
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True

    def minimize(_):
        page.window_minimized = True
        page.update()

    def close_app(_):
        running_log("关闭")
        page.controls[1].save_app_config()
        page.window.close()

    def egg(_):
        title = page.controls[0].controls[1].content.content
        old_title = title.value
        egg_list = [
            "There is something buried underneath your feet",
            "GOD god God GOD god God GOD god God GOD god God",
            "why everything needs to hurt so much.",
            "JUMP JUMP JUMP JUMP JUMP JUMP JUMP JUMP JUMP",
            "///////////////////////CONGRATULATIONS",
            ":):):):):):):):):):):):):):):):):):)"
        ]
        title.value = egg_list[random.randint(0, 5)]
        title.update()
        time.sleep(0.001)
        title.value = ""
        title.update()

    page.add(
        ft.Row(
            [
                ft.GestureDetector(
                    content=ft.Image(
                        src='assets/icon.png',
                        tooltip="RTM"
                    ),
                    on_tap=lambda _: os.system("start https://github.com/O5-7/renpy_translation_manager"),
                    on_scroll=egg,
                    multi_tap_touches=23
                ),
                ft.WindowDragArea(
                    ft.Container(
                        ft.Text("", color="#000000", size=30, offset=(0, -0.1)),
                        # ft.Text(os.getcwd(), color="#000000", size=30, offset=(0, -0.1)),
                        bgcolor="#FFFFFF",
                        height=40,
                    ),
                    expand=True,
                ),
                ft.IconButton(
                    ft.icons.MINIMIZE,
                    icon_color="#FFFFFF",
                    on_click=minimize,
                    style=ft.ButtonStyle(
                        shape={
                            ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                        }
                    ),
                    tooltip="最小化"
                ),
                ft.IconButton(
                    ft.icons.CLOSE,
                    icon_color="#e00a00",
                    on_click=close_app,
                    style=ft.ButtonStyle(
                        shape={
                            ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                        }
                    ),
                    tooltip="关闭",
                )
            ],
            spacing=0
        ),
        RPY_manager(page)
    )
    page.spacing = 0
    page.bgcolor = "#2b2b2b"

    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1500
    page.window.height = 965

    page.window.resizable = False
    page.window.center()

    page.controls[1].load_config()
    page.update()
    running_log("启动成功")


print("")
running_log("程序入口")
ft.app(target=main)
