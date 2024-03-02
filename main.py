from RPY_manager import RPY_manager
import flet as ft


def main(page: ft.Page):
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True

    def minimize(e):
        page.window_minimized = True
        page.update()

    def close(e):
        page.window_close()
        page.controls[1].save_app_config()

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
                        ft.Text("RPY Manager", color="#000000", size=30, offset=(0,-0.1)),
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
                    on_click=close,
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


ft.app(target=main)
