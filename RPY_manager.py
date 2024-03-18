import hashlib

from rpy_version import rpy_version
import flet as ft
import time
import datetime
import json
import os
from rpy_translate_task import date_format, rpy_translation_task
from running_log import running_log


class RPY_manager(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.main_page = None
        self.main_page: ft.Row
        self.page = page
        self.version_list = {}
        self.app_config = json.load(open('assets/app_config.json', mode='r', encoding='utf-8'))
        self.selected_version = ''
        self.selected_task = ''
        self.user_name = ''
        self.name_dict = {}
        self.get_name_dict()

        self.temp_path = os.getcwd()

        def filepicker_path_to_version_dialog(e: ft.FilePickerResultEvent):
            if e.path is None:
                return
            Column_controls = self.version_add_dialog.actions[0].content.controls
            Column_controls[0].controls[0].value = e.path
            Column_controls[0].controls[0].update()
            Column_controls[1].value = os.path.split(e.path)[-1]
            Column_controls[1].on_change(Column_controls[1])
            Column_controls[1].update()
            version_name_path_check(None)

        self.file_picker = ft.FilePicker(
            on_result=filepicker_path_to_version_dialog
        )

        def version_name_path_check(_):
            Column_controls = self.version_add_dialog.actions[0].content.controls
            folder_path = Column_controls[0].controls[0].value
            version_name = Column_controls[1].value

            if folder_path in [ver.folder_path for ver in self.version_list.values()]:
                Column_controls[0].controls[0].color = "#ba1a1a"
                Column_controls[0].controls[0].border_color = "#ba1a1a"
                Column_controls[0].controls[0].error_text = "重复的文件夹"
                Column_controls[2].controls[0].disabled = True
            else:
                Column_controls[0].controls[0].color = "#000000"
                Column_controls[0].controls[0].border_color = "#000000"
                Column_controls[0].controls[0].error_text = ""
                Column_controls[2].controls[0].disabled = False

            if version_name in self.version_list.keys():
                Column_controls[1].color = "#ba1a1a"
                Column_controls[1].border_color = "#ba1a1a"
                Column_controls[1].error_text = "重复的版本"
                Column_controls[2].controls[0].disabled = True
            else:
                Column_controls[1].color = "#000000"
                Column_controls[1].border_color = "#000000"
                Column_controls[1].error_text = ""
                Column_controls[2].controls[0].disabled = False

            if folder_path == "":
                Column_controls[0].controls[0].color = "#ba1a1a"
                Column_controls[0].controls[0].border_color = "#ba1a1a"
                Column_controls[0].controls[0].error_text = "不能为空"
                Column_controls[2].controls[0].disabled = True

            if version_name == "":
                Column_controls[1].color = "#ba1a1a"
                Column_controls[1].border_color = "#ba1a1a"
                Column_controls[1].error_text = "不能为空"
                Column_controls[2].controls[0].disabled = True

            self.version_add_dialog.actions[0].content.update()

        def update_version_UI_list(_):
            self.main_page.controls[1].content.controls[1].controls = [version.control for version in self.version_list.values()]
            self.main_page.controls[1].content.controls[1].update()

        self.update_version_UI_list = update_version_UI_list

        def add_version(_):
            Column_controls = self.version_add_dialog.actions[0].content.controls
            path = Column_controls[0].controls[0].value
            if not os.path.isdir(path):
                running_log(f"{path} 不是一个文件夹或不存在")
                return
            name = Column_controls[1].value
            running_log(f"添加version {name}", self)
            self.version_list.update({name: rpy_version(path, name, self), })
            self.version_list = {k: self.version_list[k] for k in sorted(self.version_list, reverse=True)}
            update_version_UI_list(None)
            close_version_add_dialog(None)
            Column_controls[0].controls[0].value = Column_controls[1].value = ''

            if not self.version_list[name].success:
                # 有错误文件 不做保存
                return

            self.app_config["default_versions"] = {}
            for version_name, version_obj in self.version_list.items():
                self.app_config["default_versions"].update({version_name: version_obj.folder_path})
            self.save_app_config()

        def close_version_add_dialog(_):
            self.version_add_dialog.open = False
            self.version_add_dialog.update()

        def close_version_delete_dialog(_):
            self.version_delete_dialog.open = False
            self.version_delete_dialog.update()

        def close_v2v_transfer_dialog(_):
            self.v2v_transfer_dialog.open = False
            self.v2v_transfer_dialog.update()

        def close_add_task_dialog(_):
            self.add_task_dialog.open = False
            self.add_task_dialog.update()

        def close_t2j_transfer_dialog(_):
            self.t2j_transfer_dialog.open = False
            self.t2j_transfer_dialog.update()

        def close_merge_tasks_dialog(_):
            self.merge_tasks_dialog.open = False
            self.merge_tasks_dialog.update()

        self.page.overlay.append(self.file_picker)
        # version文件夹选择dialog
        self.version_add_dialog = ft.AlertDialog(
            title=ft.Text("选择rpy文件所在的文件夹", size=20),
            modal=True,
            actions=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.TextField(
                                        label="文件夹路径",
                                        width=450,
                                        on_change=version_name_path_check
                                    ),
                                    ft.FilePicker(),
                                    ft.IconButton(
                                        icon=ft.icons.FOLDER,
                                        on_click=lambda _: self.file_picker.get_directory_path()
                                    )
                                ]
                            ),
                            ft.TextField(
                                label="版本名称",
                                width=450,
                                on_change=version_name_path_check
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("添加", icon=ft.icons.CHECK_ROUNDED, on_click=add_version),
                                    ft.TextButton("取消", icon=ft.icons.CANCEL_ROUNDED, icon_color="#ba1a1a", on_click=close_version_add_dialog)
                                ]
                            )
                        ]
                    ),
                    width=500,
                )
            ]
        )

        self.version_delete_dialog = ft.AlertDialog(
            title=ft.Text("从列表中删除version", size=20),
            modal=True,
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            [],
                            width=500,
                            height=250,
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        ft.Row(
                            [
                                ft.TextButton(
                                    icon=ft.icons.CHECK_ROUNDED,
                                    text="确认删除",
                                    on_click=self.delete_version_dialog
                                ),
                                ft.TextButton(
                                    icon=ft.icons.CANCEL_ROUNDED,
                                    icon_color="#FF0000",
                                    text="取消",
                                    on_click=close_version_delete_dialog
                                ),
                            ]
                        )

                    ]
                )
            ]
        )

        self.add_task_dialog = ft.AlertDialog(
            title=ft.Text("新建任务", size=20),
            modal=True,
            actions=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Tabs(
                                selected_index=0,
                                animation_duration=0,
                                tabs=[
                                    ft.Tab(
                                        text="修改",
                                        content=ft.Column(
                                            controls=[
                                                ft.Divider(),
                                                ft.Dropdown(
                                                    width=300,
                                                    label="rpy文件",
                                                    options=[],
                                                    on_change=self.update_event_dropdown
                                                ),
                                                ft.Dropdown(
                                                    width=300,
                                                    label="事件名",
                                                    options=[],
                                                    on_change=self.update_dialogue_dropdown
                                                ),
                                                ft.Dropdown(
                                                    width=450,
                                                    label="对话",
                                                    options=[],
                                                ),
                                                ft.TextField(
                                                    width=400,
                                                    label="描述",
                                                    hint_text="输入任务描述",
                                                    on_change=self.check_task_description
                                                ),
                                                ft.Row(
                                                    [
                                                        ft.TextButton("添加", icon=ft.icons.CHECK_ROUNDED, on_click=self.add_modify_task),
                                                        ft.TextButton("取消", icon=ft.icons.CANCEL_ROUNDED, icon_color="#FF0000", on_click=close_add_task_dialog)
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                )

                                            ],
                                            height=452,
                                            width=700,
                                            spacing=10,
                                        )
                                    ),
                                    ft.Tab(
                                        text="更新",
                                        content=ft.Column(
                                            controls=[
                                                ft.Divider(),
                                                ft.Row(
                                                    [
                                                        ft.Dropdown(
                                                            width=345,
                                                            label="旧版本",
                                                            options=[],
                                                        ),
                                                        ft.Dropdown(
                                                            width=345,
                                                            label="新版本",
                                                            options=[],
                                                        ),
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.TextButton("计算", icon=ft.icons.LIGHTBULB_ROUNDED, icon_color="#ff453a", on_click=self.update_task_info),
                                                        ft.TextButton("添加", icon=ft.icons.CHECK_ROUNDED, on_click=self.add_update_task),
                                                        ft.TextButton("取消", icon=ft.icons.CANCEL_ROUNDED, icon_color="#FF0000", on_click=close_add_task_dialog)
                                                    ]
                                                ),
                                                ft.Column(
                                                    [
                                                        ft.Markdown(
                                                            selectable=True,
                                                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                                            code_theme="atom-one-dark",
                                                            code_style=ft.TextStyle(font_family="Roboto Mono", size=17),
                                                        ),
                                                    ],
                                                    height=320,
                                                    scroll=ft.ScrollMode.ALWAYS
                                                ),
                                                ft.Text(visible=False)
                                            ],
                                            height=452,
                                            width=700,
                                            spacing=10,
                                        )
                                    ),
                                ]
                            ),
                        ]
                    ),
                    height=500,
                    width=700
                )]
        )

        self.setting_config_dialog = ft.AlertDialog(
            title=ft.Text("设置", size=20),
            modal=True,
            actions=[
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("用户名=", font_family="Consolas", size=20),
                                    ft.TextField(label="用户名", width=200)
                                ],
                                spacing=5
                            ),
                            ft.Row(
                                [
                                    ft.Text("自动保存=", font_family="Consolas", size=20),
                                    ft.TextField(label="间隔", suffix_text="秒", width=100)
                                ],
                                spacing=5
                            ),
                            ft.Row(
                                [
                                    ft.Text("游戏根目录=", font_family="Consolas", size=20),
                                    ft.TextField(label="游戏根目录", hint_text="绝对路径", width=400)
                                ],
                                spacing=5
                            ),
                            ft.Row(
                                [
                                    ft.Text("app_id=", font_family="Consolas", size=20),
                                    ft.TextField(label="appid", hint_text="appid", width=400)
                                ],
                                spacing=5
                            ),
                            ft.Row(
                                [
                                    ft.Text("app_key=", font_family="Consolas", size=20),
                                    ft.TextField(label="appkey", hint_text="appkey", width=400)
                                ],
                                spacing=5
                            ),
                            ft.TextButton(
                                icon=ft.icons.CHECK_ROUNDED,
                                text="保存",
                                on_click=self.save_setting_config,
                                height=50
                            )
                        ],
                    ),
                    height=400,
                    width=600,
                ),
            ]
        )

        self.t2j_transfer_dialog = ft.AlertDialog(
            title=ft.Text("转移任务翻译", size=20),
            modal=True,
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            height=450,
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        ft.Row(
                            [
                                ft.TextButton(
                                    icon=ft.icons.CHECK_ROUNDED,
                                    text="转移翻译到json",
                                    on_click=self.transfer_task_result_to_json_file
                                ),
                                ft.TextButton(
                                    icon=ft.icons.CANCEL_ROUNDED,
                                    icon_color="#FF0000",
                                    text="取消",
                                    on_click=close_t2j_transfer_dialog
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )

                    ],
                    height=500,
                    width=600,
                ),
            ]
        )

        self.v2v_transfer_dialog = ft.AlertDialog(
            title=ft.Text("版本翻译转移", size=20),
            modal=True,
            actions=[
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Dropdown(width=270),
                                ft.Icon(ft.icons.ARROW_FORWARD_ROUNDED),
                                ft.Dropdown(width=270),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.TextButton(
                                    icon=ft.icons.CHECK_ROUNDED,
                                    text="转移",
                                    on_click=self.transfer_version_translation
                                ),
                                ft.Checkbox(
                                    label="覆盖",
                                    value=False
                                ),
                                ft.Container(
                                    height=1,
                                    width=200,
                                ),
                                ft.TextButton(
                                    icon=ft.icons.CANCEL_ROUNDED,
                                    icon_color="#FF0000",
                                    text="取消",
                                    on_click=close_v2v_transfer_dialog
                                ),
                            ]
                        ),
                        ft.ProgressBar(width=510, height=20)
                    ],
                    spacing=5,
                    width=600,
                ),
            ],
        )

        self.merge_tasks_dialog = ft.AlertDialog(
            title=ft.Text("选择要合并的任务", size=20),
            modal=True,
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            height=400,
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        ft.TextField(label="新描述"),
                        ft.Row(
                            [
                                ft.TextButton(
                                    icon=ft.icons.CALL_MERGE_ROUNDED,
                                    text="合并任务",
                                    on_click=self.merge_tasks
                                ),
                                ft.TextButton(
                                    icon=ft.icons.CANCEL_ROUNDED,
                                    icon_color="#FF0000",
                                    text="取消",
                                    on_click=close_merge_tasks_dialog
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )

                    ],
                    height=500,
                    width=600,
                ),
            ]
        )

    def close_app(self, _):
        running_log("关闭")
        self.page.controls[1].save_app_config()
        self.page.window_close()

    def build(self):
        Setting_column = ft.Column(
            [
                ft.Column(
                    [
                        ft.IconButton(
                            icon=ft.icons.SETTINGS_ROUNDED,
                            icon_color="#eb9da5",
                            icon_size=34,
                            style=ft.ButtonStyle(
                                shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5)},
                                bgcolor={ft.MaterialState.DEFAULT: "#71363c"},
                            ),
                            on_click=self.open_setting_config,
                            tooltip="设置"
                        ),
                        ft.IconButton(
                            icon=ft.icons.FOLDER_SPECIAL,
                            icon_color="#eb9da5",
                            icon_size=34,
                            style=ft.ButtonStyle(
                                shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5)},
                                bgcolor={ft.MaterialState.DEFAULT: "#71363c"},
                            ),
                            on_click=lambda _: os.system(f"explorer {self.temp_path}"),
                            tooltip="打开缓存文件夹"
                        ),
                        ft.IconButton(
                            icon=ft.icons.DEVELOPER_MODE_ROUNDED,
                            icon_color="#eb9da5",
                            icon_size=34,
                            style=ft.ButtonStyle(
                                shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5)},
                                bgcolor={ft.MaterialState.DEFAULT: "#71363c"},
                            ),
                            on_click=lambda _: os.system(f"notepad {os.path.join(self.temp_path, 'out.log')}") if os.path.isfile(os.path.join(self.temp_path, 'out.log')) else lambda _: None,
                            tooltip="打开运行日志"
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Column(
                    [
                        ft.IconButton(
                            icon=ft.icons.POWER_SETTINGS_NEW_ROUNDED,
                            icon_size=34,
                            icon_color="#eb9da5",
                            style=ft.ButtonStyle(
                                shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5)},
                                bgcolor={ft.MaterialState.DEFAULT: "#71363c"},
                            ),
                            on_click=self.close_app,
                            tooltip="退出"
                        ),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            height=890,
            width=50
        )

        version_column = ft.Column(
            [
                ft.Container(
                    content=ft.Stack(
                        controls=[
                            ft.IconButton(
                                ft.icons.ADD_ROUNDED,
                                icon_size=30,
                                icon_color="#83EBAC",
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                    }
                                ),
                                on_click=self.open_version_folder_pick,
                                tooltip="添加"
                            ),
                            ft.IconButton(
                                ft.icons.DELETE_OUTLINE_ROUNDED,
                                icon_size=30,
                                icon_color="#83EBAC",
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                    }
                                ),
                                offset=(1, 0),
                                tooltip="删除",
                                on_click=self.open_delete_version_dialog
                            ),
                            ft.IconButton(
                                ft.icons.COMPARE_ARROWS_ROUNDED,
                                icon_size=30,
                                icon_color="#83EBAC",
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                    }
                                ),
                                offset=(0, 1),
                                tooltip="转移翻译",
                                on_click=self.open_v2v_transfer_dialog
                            ),
                            ft.IconButton(
                                ft.icons.REFRESH_ROUNDED,
                                # icon_color="#83EBAC",
                                icon_color="#a7a7a7",
                                icon_size=30,
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                    }
                                ),
                                offset=(1, 1),
                                tooltip="刷新 未实现",
                                disabled=True
                                # TODO: 刷新
                            ),
                        ]
                    ),
                    width=100,
                    height=100,
                    bgcolor="#007a27",
                    border=ft.border.all(3, "#83ebac"),
                    border_radius=3
                ),
                ft.Column(
                    controls=[version.control for version in self.version_list.values()],  # 所有version的control
                    spacing=5
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            height=880,
        )

        files = ft.Container(
            ft.Column(
                [
                    ft.Container(
                        ft.Row(
                            controls=[
                                ft.TextField(
                                    height=50,
                                    width=150,
                                    color="white",
                                    on_change=self.rpy_file_filter,
                                    hint_text="检索",
                                    hint_style=ft.TextStyle(color="#409BDC")
                                ),
                                ft.PopupMenuButton(
                                    items=[
                                        ft.PopupMenuItem(
                                            content=ft.Text(
                                                value="谨慎操作",
                                                color="#FF0000",
                                                size=20
                                            ),
                                        ),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.FOLDER_OPEN,
                                            on_click=lambda _: os.system(f"explorer {self.version_list[self.selected_version].folder_path if self.selected_version != '' else ''}"),
                                            text="打开文件夹",
                                        ),
                                        ft.PopupMenuItem(),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.ARROW_FORWARD_IOS_ROUNDED,
                                            text="json到rpy",
                                            on_click=lambda _: self.version_list[self.selected_version].json_2_rpy()
                                        ),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                                            text="rpy到json",
                                            on_click=lambda _: self.version_list[self.selected_version].rpy_2_json()
                                        ),
                                        # ft.FilePicker()
                                    ],
                                    content=ft.Icon(
                                        name=ft.icons.MENU_ROUNDED,
                                        size=30,
                                        color="#409bdc",
                                        tooltip="文件管理"
                                    ),
                                )
                            ],
                            width=200,
                            height=50,
                            spacing=7,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        border=ft.border.all(3, "#409bdc"),
                        border_radius=3,
                        margin=0,
                        padding=0,
                    ),
                    ft.Column(
                        controls=[],
                        height=366,
                        scroll=ft.ScrollMode.ALWAYS,
                        spacing=5
                    ),
                ],
                spacing=5
            ),
            height=445,
        )

        tasks = ft.Container(
            ft.Column(
                [
                    ft.Container(
                        ft.Row(
                            controls=[
                                ft.TextField(
                                    height=50,
                                    width=150,
                                    color="white",
                                    on_change=self.task_filter,
                                    hint_text="检索",
                                    hint_style=ft.TextStyle(color="#409BDC")
                                ),
                                ft.PopupMenuButton(
                                    items=[
                                        ft.PopupMenuItem(
                                            icon=ft.icons.REFRESH_ROUNDED,
                                            on_click=self.refresh_tasks,
                                            text="刷新任务",
                                        ),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.FOLDER_OPEN,
                                            on_click=lambda _: os.system(f"explorer {os.path.join(self.version_list[self.selected_version].folder_path, 'tasks') if self.selected_version != '' else ''}"),
                                            text="打开任务文件夹",
                                        ),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.CABLE,
                                            on_click=self.open_t2j_transfer_dialog,
                                            text="提交任务",
                                        ),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.ADD_ROUNDED,
                                            on_click=self.open_add_task,
                                            text="添加任务"
                                        ),
                                        ft.PopupMenuItem(
                                            icon=ft.icons.CALL_MERGE_SHARP,
                                            on_click=self.open_merge_task,
                                            text="合并任务"
                                        ),
                                    ],
                                    content=ft.Icon(
                                        name=ft.icons.MENU_ROUNDED,
                                        size=30,
                                        color="#409bdc",
                                        tooltip="任务管理"
                                    ),
                                )
                            ],
                            width=200,
                            height=50,
                            spacing=7
                        ),
                        border=ft.border.all(3, "#409bdc"),
                        border_radius=3,
                        margin=0,
                        padding=0,
                    ),
                    ft.Column(
                        controls=[],
                        height=366,
                        scroll=ft.ScrollMode.ALWAYS,
                        spacing=5,
                    ),
                ],
                spacing=5,
            ),
            height=445,
        )

        TEXT_editor = ft.Container(
            ft.Container(width=1060, height=890, bgcolor="#eeeeee"),
            border_radius=5,
            border=ft.border.all(5, "#ff7f00")
        )
        self.main_page = ft.Row(
            [
                ft.Container(
                    Setting_column,
                    bgcolor="#71363c",
                    border=ft.border.all(5, "#eb9da5"),
                    border_radius=5,
                    width=60,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    version_column,
                    bgcolor="#16712f",
                    border=ft.border.all(5, "#4dc072"),
                    border_radius=5,
                    padding=5,
                    width=120,
                    alignment=ft.alignment.center
                ),
                ft.Column(
                    [
                        ft.Container(
                            files,
                            bgcolor="#1c3371",
                            border=ft.border.all(5, "#5d8fc0"),
                            border_radius=5,
                            padding=5,
                            width=220,
                            height=447.5,
                            alignment=ft.alignment.center
                        ),
                        ft.Container(
                            tasks,
                            bgcolor="#1c3371",
                            border=ft.border.all(5, "#5d8fc0"),
                            border_radius=5,
                            padding=5,
                            width=220,
                            height=447.5,
                            alignment=ft.alignment.center
                        ),
                    ],
                    spacing=5
                ),
                TEXT_editor
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        return self.main_page

    def get_name_dict(self):
        running_log("尝试读取人名对照表")
        if self.app_config["game_path"] == "":
            running_log("失败 请设置游戏根目录")
            return
        def_file_path = os.path.join(self.app_config["game_path"], "game/definitions.rpy")
        if not os.path.isfile(def_file_path):
            running_log("失败 definitions.rpy不存在")
            return
        with open(def_file_path, mode="r", encoding='utf-8') as F:
            def absolute(_):
                pass

            class Character:
                def __init__(self, name, color="", who_outlines=None, who_font=None, ):
                    self.name = name
                    self.color = color

                def get_name_color(self):
                    return [self.name, self.color]

            for line in F.readlines():
                line: str
                if line.find("Character(") != -1:
                    line = line[11:-1]
                    ed_index = line.find("=")
                    key = line[:ed_index - 1]
                    char_obj_str = line[ed_index + 2:]
                    char_obj = eval(char_obj_str)
                    self.name_dict.update({key: char_obj.get_name_color()})

    def open_version_folder_pick(self, _):
        self.page.dialog = self.version_add_dialog
        self.version_add_dialog.open = True
        self.page.update()

    def open_delete_version_dialog(self, _):
        checkbox_Column = self.version_delete_dialog.actions[0].controls[0]
        checkbox_Column.controls = []
        for version_name, version_obj in self.version_list.items():
            checkbox_Column.controls.append(
                ft.Row(
                    [
                        ft.Checkbox(),
                        ft.Text(version_name, size=20),
                        ft.Text(f"文件数:{len(version_obj.rpy_dict)}"),
                        ft.Text(f"任务数:{len(version_obj.tasks_dict)}")
                    ],
                    spacing=10
                )
            )

        self.page.dialog = self.version_delete_dialog
        self.version_delete_dialog.open = True
        self.page.update()

    def delete_version_dialog(self, _):
        running_log(f"尝试删除version", self)
        checkbox_Column = self.version_delete_dialog.actions[0].controls[0]
        for Row in checkbox_Column.controls:
            checkbox, version_name_text, _, _ = Row.controls
            if checkbox.value:
                version_name = version_name_text.value
                running_log(f"删除version {version_name}", self)
                del self.version_list[version_name]

                if self.selected_version == version_name:
                    self.page.controls[0].controls[1].content.content.value = f"RTM"
                    self.page.controls[0].controls[1].content.content.update()

                    files_column = self.main_page.controls[2].controls[0].content.content.controls[1]
                    task_column = self.main_page.controls[2].controls[1].content.content.controls[1]
                    text_con = self.main_page.controls[3]

                    files_column.controls = []
                    task_column.controls = []
                    text_con.content = ft.Container(
                        ft.Container(width=1060, height=890, bgcolor="#eeeeee"),
                        border_radius=5,
                        border=ft.border.all(5, "#ff7f00")
                    )

                    task_column.update()
                    files_column.update()
                    text_con.update()

        self.version_list = {k: self.version_list[k] for k in sorted(self.version_list, reverse=True)}
        self.update_version_UI_list(None)

        self.app_config["default_versions"] = {}
        for version_name, version_obj in self.version_list.items():
            self.app_config["default_versions"].update({version_name: version_obj.folder_path})
        self.save_app_config()

        self.version_delete_dialog.open = False
        self.page.update()

    def open_add_task(self, _):
        if self.selected_version == "":
            return
        rpy_file_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[1]
        rpy_file_dropdown.options = [ft.dropdown.Option(rpy_name) for rpy_name in self.version_list[self.selected_version].rpy_dict.keys()]

        version_dropdown_controls = self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[1].controls
        version_dropdown_controls[0].options = [ft.dropdown.Option(version_name) for version_name in self.version_list.keys()]
        version_dropdown_controls[1].options = [ft.dropdown.Option(version_name) for version_name in self.version_list.keys()]
        version_dropdown_controls[1].value = self.selected_version

        self.page.dialog = self.add_task_dialog
        self.add_task_dialog.open = True
        self.page.update()

    def update_event_dropdown(self, _):
        rpy_file_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[1]
        event_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[2]
        selected_rpy_file = rpy_file_dropdown.value
        event_dropdown.options = [ft.dropdown.Option(event_name) for event_name in self.version_list[self.selected_version].rpy_dict[selected_rpy_file].file_json['dialogue'].keys()]
        event_dropdown.options.append(ft.dropdown.Option("strings"))
        event_dropdown.update()

    def update_dialogue_dropdown(self, _):
        rpy_file_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[1]
        event_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[2]
        dialogue_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[3]
        selected_event = event_dropdown.value
        if not selected_event == "strings":
            dialogue_dropdown.options = [
                ft.dropdown.Option(f"{k}: {v['origin'][:40]}")
                for k, v
                in self.version_list[self.selected_version].rpy_dict[rpy_file_dropdown.value].file_json['dialogue'][selected_event].items()
            ]
            dialogue_dropdown.options.insert(0, ft.dropdown.Option(f"ALL"))
            dialogue_dropdown.value = "ALL"
            dialogue_dropdown.disable = False
        else:
            dialogue_dropdown.options = [ft.dropdown.Option("ALL")]
            dialogue_dropdown.value = "ALL"
            for strings in self.version_list[self.selected_version].rpy_dict[rpy_file_dropdown.value].file_json['strings']:
                for string in strings:
                    dialogue = hashlib.md5(string["old"].encode("utf-8")).hexdigest()[:8]
                    dialogue_dropdown.options.append(
                        ft.dropdown.Option(f"{dialogue}: {string['old'][:40]}")
                    )
        dialogue_dropdown.update()

    def check_task_description(self, _):
        task_description_textfield = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[4]
        if task_description_textfield.value.find("@") != -1:
            task_description_textfield.error_text = "不要包含@"
        else:
            task_description_textfield.error_text = ""
        task_description_textfield.update()

    def add_modify_task(self, _):
        running_log(f"尝试添加润色任务", self)
        add_modify_task_3_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls
        rpy_file_name = add_modify_task_3_dropdown[1].value
        event_name = add_modify_task_3_dropdown[2].value
        dialogue_name = add_modify_task_3_dropdown[3].value[:8]
        description = add_modify_task_3_dropdown[4].value
        if description == "" or description is None:
            add_modify_task_3_dropdown[4].error_text = "请输入描述"
            add_modify_task_3_dropdown[4].update()
            return
        else:
            add_modify_task_3_dropdown[4].error_text = ""
            add_modify_task_3_dropdown[4].update()

        if any([i is None for i in [rpy_file_name, event_name, dialogue_name, description]]):
            return

        running_log(f"添加润色任务 {description}", self)

        if not all([rpy_file_name, event_name, dialogue_name, description]):
            return

        host_date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
        task_hex = hashlib.md5(f"{rpy_file_name}{event_name}{dialogue_name}{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
        task_hex = task_hex[:8]

        task = {
            "host_name": self.user_name,
            "host_date": host_date,
            "worker_name": "",
            "last_change_date": "",
            "hex": task_hex,
            "task_type": "modify",
            "description": description,
            "task_content": {
                rpy_file_name: {
                    event_name: [dialogue_name]
                }
            },
            "task_result": {}
        }

        file_name = f"{description}@{task_hex}.json"
        file_path = os.path.join(self.version_list[self.selected_version].folder_path, "tasks", file_name)

        with open(file_path, mode='w', encoding='utf-8') as F:
            F.write(json.dumps(task, indent=2, ensure_ascii=False))

        while not os.path.isfile(file_path):
            pass
        tasks_dick = self.version_list[self.selected_version].tasks_dict
        tasks_dick.update(
            {task_hex: rpy_translation_task(file_path, self)}
        )

        tasks_dick = {k: tasks_dick[k] for k in sorted(tasks_dick, reverse=True, key=lambda t: datetime.datetime.strptime(tasks_dick[t].host_date, date_format).timestamp())}
        self.version_list[self.selected_version].update_control()
        self.update_version_UI_list(None)

        task_column = self.main_page.controls[2].controls[1].content.content.controls[1]
        task_column.controls = [task_obj.control for task_obj in tasks_dick.values()]
        task_column.update()

        self.add_task_dialog.open = False
        self.page.update()

    def add_update_task(self, _):
        running_log("尝试添加更新任务", self)
        tasks_dick = self.version_list[self.selected_version].tasks_dict

        task_info = self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[4].value

        if task_info is None:
            return
        task_info: str
        print(task_info)
        new_file, new_event, modify_line, new_or_modify_string = task_info.split("[%split^]")

        new_file = eval(new_file)
        new_event = eval(new_event)
        modify_line = eval(modify_line)
        new_or_modify_string = eval(new_or_modify_string)

        host_date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
        for file_name in new_file:
            for event_name in self.version_list[self.selected_version].rpy_dict[file_name].file_json['dialogue'].keys():
                description = f"新文件_{file_name}_{event_name}"
                task_hex = hashlib.md5(f"{file_name}{event_name}{'ALL'}{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
                task_hex = task_hex[:8]
                task_file_name = f"{description}@{task_hex}.json"
                file_path = os.path.join(self.version_list[self.selected_version].folder_path, "tasks", task_file_name)

                new_file_task = {
                    "host_name": self.user_name,
                    "host_date": host_date,
                    "worker_name": "",
                    "last_change_date": "",
                    "hex": task_hex,
                    "task_type": "update",
                    "description": description,
                    "task_content": {
                        file_name: {event_name: ["ALL"]}
                    },
                    "task_result": {}
                }

                with open(file_path, mode='w', encoding='utf-8') as F:
                    F.write(json.dumps(new_file_task, indent=2, ensure_ascii=False))

                tasks_dick.update(
                    {task_hex: rpy_translation_task(file_path, self)}
                )

        for file_name, event_names in new_event.items():
            for event_name in event_names:
                description = f"新事件_{file_name}_{event_name}"
                task_hex = hashlib.md5(f"{file_name}{event_name}{'ALL'}{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
                task_hex = task_hex[:8]
                task_file_name = f"{description}@{task_hex}.json"
                file_path = os.path.join(self.version_list[self.selected_version].folder_path, "tasks", task_file_name)

                new_file_task = {
                    "host_name": self.user_name,
                    "host_date": host_date,
                    "worker_name": "",
                    "last_change_date": "",
                    "hex": task_hex,
                    "task_type": "update",
                    "description": description,
                    "task_content": {
                        file_name: {event_name: ["ALL"]}
                    },
                    "task_result": {}
                }

                with open(file_path, mode='w', encoding='utf-8') as F:
                    F.write(json.dumps(new_file_task, indent=2, ensure_ascii=False))

                tasks_dick.update(
                    {task_hex: rpy_translation_task(file_path, self)}
                )

        for file_name, event_name, lines in modify_line:
            description = f"更改对话_{file_name}_{event_name}"
            task_hex = hashlib.md5(f"{file_name}{event_name}{''.join(lines)}{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
            task_hex = task_hex[:8]
            task_file_name = f"{description}@{task_hex}.json"
            file_path = os.path.join(self.version_list[self.selected_version].folder_path, "tasks", task_file_name)

            new_file_task = {
                "host_name": self.user_name,
                "host_date": host_date,
                "worker_name": "",
                "last_change_date": "",
                "hex": task_hex,
                "task_type": "update",
                "description": description,
                "task_content": {
                    file_name: {event_name: lines}
                },
                "task_result": {}
            }

            with open(file_path, mode='w', encoding='utf-8') as F:
                F.write(json.dumps(new_file_task, indent=2, ensure_ascii=False))

            tasks_dick.update(
                {task_hex: rpy_translation_task(file_path, self)}
            )

        for file_name, strings in new_or_modify_string.items():
            description = f"更新string_{file_name}"
            task_hex = hashlib.md5(f"{file_name}strings{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
            task_hex = task_hex[:8]
            task_file_name = f"{description}@{task_hex}.json"
            file_path = os.path.join(self.version_list[self.selected_version].folder_path, "tasks", task_file_name)

            new_file_task = {
                "host_name": self.user_name,
                "host_date": host_date,
                "worker_name": "",
                "last_change_date": "",
                "hex": task_hex,
                "task_type": "update",
                "description": description,
                "task_content": {
                    file_name: {"strings": [hashlib.md5(s.encode(encoding='UTF-8')).hexdigest()[:8] for s in strings]}
                },
                "task_result": {}
            }

            with open(file_path, mode='w', encoding='utf-8') as F:
                F.write(json.dumps(new_file_task, indent=2, ensure_ascii=False))

            tasks_dick.update(
                {task_hex: rpy_translation_task(file_path, self)}
            )

        tasks_dick = {k: tasks_dick[k] for k in sorted(tasks_dick, reverse=True, key=lambda t: datetime.datetime.strptime(tasks_dick[t].host_date, date_format).timestamp())}
        for version_obj in self.version_list.values():
            version_obj.update_control()
        self.update_version_UI_list(None)

        task_column = self.main_page.controls[2].controls[1].content.content.controls[1]
        task_column.controls = [task_obj.control for task_obj in tasks_dick.values()]
        task_column.update()

        self.add_task_dialog.open = False
        self.add_task_dialog.update()

    def update_task_info(self, _):
        running_log("计算更新内容", self)
        add_update_task_Column = self.add_task_dialog.actions[0].content.controls[0].tabs[1].content
        old_version = add_update_task_Column.controls[1].controls[0].value
        new_version = add_update_task_Column.controls[1].controls[1].value
        if old_version is None or new_version is None:
            return
        new_file = set(self.version_list[new_version].rpy_dict.keys()) - set(self.version_list[old_version].rpy_dict.keys())
        new_event = {}
        change_line = []
        modify_or_new_strings = {}

        for file_name in set(self.version_list[new_version].rpy_dict.keys()) & set(self.version_list[old_version].rpy_dict.keys()):
            new_event_for_file = set(self.version_list[new_version].rpy_dict[file_name].file_json['dialogue'].keys()) - set(self.version_list[old_version].rpy_dict[file_name].file_json['dialogue'].keys())
            if len(new_event_for_file) != 0:
                new_event.update({file_name: list(new_event_for_file)})
            old_strings_set = set()
            new_strings_set = set()
            for tr_list in self.version_list[new_version].rpy_dict[file_name].file_json["strings"]:
                for one_string in tr_list:
                    new_strings_set.add(one_string["old"])
            for tr_list in self.version_list[old_version].rpy_dict[file_name].file_json["strings"]:
                for one_string in tr_list:
                    old_strings_set.add(one_string["old"])
            new_strings_set = new_strings_set - old_strings_set
            if len(new_strings_set) != 0:
                modify_or_new_strings.update({file_name: list(new_strings_set)})
            for event_name in set(self.version_list[new_version].rpy_dict[file_name].file_json['dialogue'].keys()) & set(self.version_list[old_version].rpy_dict[file_name].file_json['dialogue'].keys()):
                change_line_for_event = set(self.version_list[new_version].rpy_dict[file_name].file_json['dialogue'][event_name].keys()) - set(self.version_list[old_version].rpy_dict[file_name].file_json['dialogue'][event_name].keys())
                if len(change_line_for_event) != 0:
                    change_line.append([file_name, event_name, list(change_line_for_event)])

        hint_text_1 = f"新文件:{len(new_file)}:\n{new_file}"
        hint_text_2 = f"旧文件的新事件:{sum([len(v) for k, v in new_event.items()])}:\n{new_event}"
        hint_text_3 = f"更改的对话:{sum([len(event[2]) for event in change_line])}:\n{change_line}"
        hint_text_4 = f"更新或增加的string:{sum([len(v) for k, v in modify_or_new_strings.items()])}:\n" + "\n".join([f"{k}:{v}" for k, v in modify_or_new_strings.items()])

        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[3].controls[0].value = '\n'.join(['```python', hint_text_1, hint_text_2, hint_text_3, hint_text_4, '```'])
        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[4].value = "[%split^]".join([f"{new_file}", f"{new_event}", f"{change_line}", f"{modify_or_new_strings}"])
        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[3].controls[0].update()
        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[4].update()

    def save_app_config(self):
        running_log("保存设置到本地")
        with open('assets/app_config.json', mode='w', encoding='utf-8') as F:
            F.write(json.dumps(self.app_config, indent=2, ensure_ascii=False))

    def rpy_file_filter(self, e):
        text_filter = e.control.value.lower()
        controls = self.main_page.controls[2].controls[0].content.content.controls[1].controls
        for rpy_file_control in controls:
            rpy_file_control.visible = False if (rpy_file_control.content.content.controls[0].controls[0]).value.lower().find(text_filter) == -1 else True
        self.main_page.controls[2].controls[0].content.content.controls[1].update()

    def task_filter(self, e):
        text_filter = e.control.value.lower()
        controls = self.main_page.controls[2].controls[1].content.content.controls[1].controls
        for task_control in controls:
            task_control.visible = False if (task_control.content.content.controls[-1]).value.lower().find(text_filter) == -1 else True
        self.main_page.controls[2].controls[1].content.content.controls[1].update()

    def load_config(self):
        self.user_name = self.app_config['user_name']
        for name, path in self.app_config['default_versions'].items():
            if not os.path.isdir(path):
                running_log(f"{path} 不存在")
                del self.app_config['default_versions'][name]
                continue
            self.version_list.update({name: rpy_version(path, name, self)})
            self.update_version_UI_list(None)

    def open_setting_config(self, _):
        self.setting_config_dialog.actions[0].content.controls[0].controls[1].value = self.app_config["user_name"]
        self.setting_config_dialog.actions[0].content.controls[1].controls[1].value = str(self.app_config["task_auto_save"])
        self.setting_config_dialog.actions[0].content.controls[2].controls[1].value = str(self.app_config["game_path"])
        self.setting_config_dialog.actions[0].content.controls[3].controls[1].value = str(self.app_config["appid"])
        self.setting_config_dialog.actions[0].content.controls[4].controls[1].value = str(self.app_config["appkey"])
        self.page.dialog = self.setting_config_dialog
        self.setting_config_dialog.open = True
        self.page.update()

    def open_t2j_transfer_dialog(self, _):
        if self.selected_version == "":
            return
        rpy_dict = self.version_list[self.selected_version].rpy_dict
        transfer_Column = self.t2j_transfer_dialog.actions[0].controls[0]
        transfer_Column.controls = []

        for task_hex, task in self.version_list[self.selected_version].tasks_dict.items():
            acc = 0
            for file_name, event_dict in task.task_content.items():
                rpy_file = rpy_dict[file_name]
                for event_name, dialogues in event_dict.items():
                    if event_name == "strings":
                        if dialogues[0] == "ALL":
                            for strings in rpy_file.file_json["strings"]:
                                acc += len(strings)
                        else:
                            acc += len(dialogues)
                    else:
                        if dialogues[0] == "ALL":
                            acc += len(rpy_file.file_json["dialogue"][event_name])
                        else:
                            acc += len(dialogues)
            if acc != 0:
                acc = sum([sum([len(e) for e in f.values()]) for f in task.task_result.values()]) / acc

            description: str = task.description

            transfer_Column.controls.append(
                ft.Row(
                    [
                        ft.Checkbox(
                            value=acc == 1
                        ),
                        ft.Text(task_hex, visible=False),
                        ft.Text(
                            value=description,
                            font_family="黑体",
                            size=15,
                            width=400,
                        ),
                        ft.Text(
                            value=f'{round(acc * 100, 2)}'.rjust(5) + "%",
                            font_family="Consolas",
                            size=15,
                            width=60,
                            color="#FF0000" if acc == 1 else ""
                        ),
                    ]
                )
            )

        self.page.dialog = self.t2j_transfer_dialog
        self.t2j_transfer_dialog.open = True
        self.page.update()

    def open_merge_task(self, _):
        merge_Column = self.merge_tasks_dialog.actions[0].controls[0]
        merge_Column.controls = []

        for task_hex, task in self.version_list[self.selected_version].tasks_dict.items():
            description: str = task.description
            merge_Column.controls.append(
                ft.Row(
                    [
                        ft.Checkbox(),
                        ft.Text(task_hex, visible=False),
                        ft.Text(
                            value=description,
                            font_family="Consolas",
                            size=15,
                            width=400,
                        ),
                    ]
                )
            )

        self.page.dialog = self.merge_tasks_dialog
        self.merge_tasks_dialog.open = True
        self.page.update()

    def merge_tasks(self, _):
        running_log("尝试合并任务")
        need_merge_list = []

        check_boxes_column = self.merge_tasks_dialog.actions[0].controls[0]
        for row in check_boxes_column.controls:
            checkbox, task_hex, _ = row.controls
            if checkbox.value:
                need_merge_list.append(task_hex.value)
        if len(need_merge_list) <= 1:
            return

        host_date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
        description = self.merge_tasks_dialog.actions[0].controls[1].value
        task_name = "_".join(need_merge_list)

        if description == "":
            self.merge_tasks_dialog.actions[0].controls[1].error_text = "请输入描述"
            self.merge_tasks_dialog.actions[0].controls[1].update()
            return
        else:
            self.merge_tasks_dialog.actions[0].controls[1].error_text = ""
            self.merge_tasks_dialog.actions[0].controls[1].update()
        new_task_hex = hashlib.md5(f"{task_name}{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
        new_task_hex = new_task_hex[:8]
        task_file_name = f"{description}@{new_task_hex}.json"
        file_path = os.path.join(self.version_list[self.selected_version].folder_path, "tasks", task_file_name)

        new_file_task = {
            "host_name": self.user_name,
            "host_date": host_date,
            "worker_name": "merge_tasks",
            "last_change_date": "",
            "hex": new_task_hex,
            "task_type": "merge",
            "description": description,
            "task_content": {},
            "task_result": {}
        }

        running_log(f"合并任务{need_merge_list}")
        for merge_task_hex in need_merge_list:
            merge_task = self.version_list[self.selected_version].tasks_dict[merge_task_hex]

            # 任务描述合并
            for file_name, events in merge_task.task_content.items():
                if file_name not in new_file_task["task_content"].keys():
                    new_file_task["task_content"].update({file_name: {}})
                for event_name, dialogs in events.items():
                    if event_name not in new_file_task["task_content"][file_name].keys():
                        new_file_task["task_content"][file_name].update({event_name: []})
                    exist_dialog = new_file_task["task_content"][file_name][event_name]
                    if dialogs[0] == "ALL":
                        new_file_task["task_content"][file_name][event_name] = ["ALL"]
                    elif len(exist_dialog) == 0 or exist_dialog[0] != "ALL":
                        new_file_task["task_content"][file_name][event_name] = list(set(exist_dialog) | set(dialogs))

            for file_name, events in merge_task.task_result.items():
                if file_name not in new_file_task["task_result"].keys():
                    new_file_task["task_result"].update({file_name: {}})
                for event_name, dialogs in events.items():
                    if event_name not in new_file_task["task_result"][file_name].keys():
                        new_file_task["task_result"][file_name].update({event_name: {}})
                    new_file_task["task_result"][file_name][event_name].update(dialogs)

        with open(file_path, mode='w', encoding='utf-8') as F:
            F.write(json.dumps(new_file_task, indent=2, ensure_ascii=False))

        tasks_dick = self.version_list[self.selected_version].tasks_dict
        tasks_dick.update(
            {new_task_hex: rpy_translation_task(file_path, self)}
        )

        tasks_dick = {k: tasks_dick[k] for k in sorted(tasks_dick, reverse=True, key=lambda t: datetime.datetime.strptime(tasks_dick[t].host_date, date_format).timestamp())}
        self.version_list[self.selected_version].update_control()
        self.update_version_UI_list(None)

        task_column = self.main_page.controls[2].controls[1].content.content.controls[1]
        task_column.controls = [task_obj.control for task_obj in tasks_dick.values()]
        task_column.update()

        self.merge_tasks_dialog.open = False
        self.page.update()

    def transfer_task_result_to_json_file(self, _):
        check_boxes_column = self.t2j_transfer_dialog.actions[0].controls[0]
        running_log(f"转移{len(check_boxes_column.controls)}个任务翻译到json", self)
        ver_obj = self.version_list[self.selected_version]
        update_rpy_set = set()
        for row in check_boxes_column.controls:
            checkbox, task_hex, _, _ = row.controls
            if checkbox.value:
                task_obj = self.version_list[self.selected_version].tasks_dict[task_hex.value]
                for file_name, event_dict in task_obj.task_result.items():
                    update_rpy_set.add(file_name)
                    for event_name, dialogue_dict in event_dict.items():
                        if event_name == "strings":
                            for dialogue, translation in dialogue_dict.items():

                                for strings_list in ver_obj.rpy_dict[file_name].file_json["strings"]:
                                    for strings in strings_list:
                                        if hashlib.md5(strings["old"].encode("utf-8")).hexdigest()[:8] == dialogue:
                                            strings["new"] = translation
                        else:
                            for dialogue, translation in dialogue_dict.items():
                                ver_obj.rpy_dict[file_name].file_json["dialogue"][event_name][dialogue]["translation"] = translation

        for file_name in update_rpy_set:
            rpy_obj = ver_obj.rpy_dict[file_name]
            rpy_obj.json_info_value = ''
            rpy_obj.rpy_info_value = ''
            rpy_obj.line_num = {
                "rpy": 0,
                "json": 0
            }
            rpy_obj.showing_type = ""
            rpy_obj.write_json(os.path.join(self.version_list[self.selected_version].folder_path))

        self.t2j_transfer_dialog.open = False
        self.page.update()

    def open_v2v_transfer_dialog(self, _):
        self.v2v_transfer_dialog.actions[0].controls[1].visible = True
        self.v2v_transfer_dialog.actions[0].controls[2].visible = False

        dropdown_row = self.v2v_transfer_dialog.actions[0].controls[0]
        dropdown_row.controls[0].options = [ft.dropdown.Option(version_name) for version_name in self.version_list.keys()]
        dropdown_row.controls[2].options = [ft.dropdown.Option(version_name) for version_name in self.version_list.keys()]

        self.page.dialog = self.v2v_transfer_dialog
        self.v2v_transfer_dialog.open = True
        self.page.update()

    def transfer_version_translation(self, _):
        is_cover = self.v2v_transfer_dialog.actions[0].controls[1].controls[1].value

        dropdown_row = self.v2v_transfer_dialog.actions[0].controls[0]
        old_version_name = dropdown_row.controls[0].value
        new_version_name = dropdown_row.controls[2].value

        if old_version_name == new_version_name or old_version_name == "" or new_version_name == "":
            return
        running_log(f"转移翻译 {old_version_name} 到 {new_version_name}", self)
        self.v2v_transfer_dialog.actions[0].controls[1].visible = False
        self.v2v_transfer_dialog.actions[0].controls[2].visible = True
        self.v2v_transfer_dialog.update()
        pb = self.v2v_transfer_dialog.actions[0].controls[2]

        for num, (rpy_name, old_rpy_obj) in enumerate(self.version_list[old_version_name].rpy_dict.items()):
            pb.value = num / len(self.version_list[old_version_name].rpy_dict)
            pb.update()
            if rpy_name in self.version_list[new_version_name].rpy_dict.keys():  # 是否包含文件
                new_rpy_obj = self.version_list[new_version_name].rpy_dict[rpy_name]
                new_rpy_obj.json_info_value = ''
                new_rpy_obj.rpy_info_value = ''
                new_rpy_obj.line_num = {
                    "rpy": 0,
                    "json": 0
                }
                new_rpy_obj.showing_type = ""

                for event_name, dialogues in old_rpy_obj.file_json['dialogue'].items():
                    if event_name in new_rpy_obj.file_json["dialogue"].keys():  # 是否包含事件
                        for dialogue_hex, dialogue in dialogues.items():
                            if dialogue_hex in self.version_list[new_version_name].rpy_dict[rpy_name].file_json["dialogue"][event_name].keys():  # 是否包含对话
                                target_dialogue = self.version_list[new_version_name].rpy_dict[rpy_name].file_json["dialogue"][event_name][dialogue_hex]
                                if is_cover or target_dialogue["translation"] == "":
                                    target_dialogue.update({"translation": dialogue["translation"]})

                for old_strings in old_rpy_obj.file_json['strings']:
                    for old_string in old_strings:
                        for new_strings in new_rpy_obj.file_json['strings']:
                            for new_string in new_strings:
                                if old_string["old"] == new_string["old"]:
                                    if new_string["new"] == "" or is_cover:
                                        new_string["new"] = old_string["new"]

                new_rpy_obj.write_json(self.version_list[new_version_name].folder_path)

        self.main_page.controls[3] = ft.Container(
            ft.Container(width=1060, height=890, bgcolor="#eeeeee"),
            border_radius=5,
            border=ft.border.all(5, "#ff7f00")
        )

        self.v2v_transfer_dialog.open = False
        self.page.update()

    def refresh_tasks(self, _):
        if self.selected_version == "":
            return
        running_log(f"刷新任务")
        self.selected_task = ""
        self.page.controls[0].controls[1].content.content.value = f"RTM >>> {self.selected_version}"
        self.page.controls[0].controls[1].content.content.update()

        self.version_list[self.selected_version].scan_tasks()
        tasks_dict = self.version_list[self.selected_version].tasks_dict
        tasks_dict = {k: tasks_dict[k] for k in sorted(tasks_dict, reverse=True, key=lambda t: datetime.datetime.strptime(tasks_dict[t].host_date, date_format).timestamp())}
        task_column = self.main_page.controls[2].controls[1].content.content.controls[1]
        task_column.controls = [task_obj.control for task_obj in tasks_dict.values()]
        for c in task_column.controls:
            c.visible = True
        task_column.update()

        self.main_page.controls[3] = ft.Container(
            ft.Container(width=1060, height=890, bgcolor="#eeeeee"),
            border_radius=5,
            border=ft.border.all(5, "#ff7f00")
        )

        for version_obj in self.version_list.values():
            version_obj.update_control()
        self.update_version_UI_list(None)
        self.main_page.update()

    def save_setting_config(self, _):
        running_log("保存设置", self)
        self.app_config["user_name"] = self.setting_config_dialog.actions[0].content.controls[0].controls[1].value
        try:
            self.app_config["task_auto_save"] = int(self.setting_config_dialog.actions[0].content.controls[1].controls[1].value)
        except ValueError:
            pass

        game_path_input = self.setting_config_dialog.actions[0].content.controls[2].controls[1].value
        if os.path.isdir(os.path.join(game_path_input, "game", "scripts")):
            self.app_config["game_path"] = game_path_input

        self.app_config["appid"] = self.setting_config_dialog.actions[0].content.controls[3].controls[1].value
        self.app_config["appkey"] = self.setting_config_dialog.actions[0].content.controls[4].controls[1].value

        self.save_app_config()
        self.setting_config_dialog.open = False
        self.page.update()


if __name__ == '__main__':
    rpy_m = RPY_manager(None)
