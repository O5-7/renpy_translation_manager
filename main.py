import os

from RPY_manager import RPY_manager
import flet as ft
from running_log import running_log


def main(page: ft.Page):
    running_log("启动 RPY_manager")
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True

    def minimize(_):
        page.window_minimized = True
        page.update()

    def close_app(_):
        running_log("关闭")
        page.controls[1].save_app_config()
        page.window_close()

    page.add(
        ft.Row(
            [
                ft.GestureDetector(
                    content=ft.Image(
                        src='assets/icon.png'
                    ),
                    on_hover=lambda _: print()
                ),
                ft.WindowDragArea(
                    ft.Container(
                        ft.Text(os.getcwd(), color="#000000", size=30, offset=(0, -0.1)),
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
    page.window_width = 1500
    page.window_height = 965

    page.window_resizable = False
    page.window_center()

    page.controls[1].load_config()
    page.update()
    running_log("启动成功")


print("")
running_log("程序入口")
ft.app(target=main)
