import hashlib

from rpy_file import RPY_File
from rpy_version import rpy_version
import flet as ft
import time
import datetime
import json
import os
from rpy_translate_task import date_format, rpy_translation_task


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

        """
        version文件夹选择
        """

        def filepicker_path_to_version_dialog(e: ft.FilePickerResultEvent):
            Column_controls = self.version_add_dialog.actions[0].content.controls
            Column_controls[0].controls[0].value = e.path
            Column_controls[0].controls[0].update()
            Column_controls[1].value = os.path.split(e.path)[-1]
            Column_controls[1].on_change(Column_controls[1])
            Column_controls[1].update()

        self.file_picker = ft.FilePicker(
            on_result=filepicker_path_to_version_dialog
        )

        def version_name_check(e):
            Column_controls = self.version_add_dialog.actions[0].content.controls
            try:
                e = e.control
            except AttributeError:
                pass

            if e.value in self.version_list.keys():
                e.color = "#ba1a1a"
                e.border_color = "#ba1a1a"
                e.error_text = "重复的版本"
                Column_controls[2].controls[0].disabled = True
            else:
                e.color = "#000000"
                e.border_color = "#000000"
                e.error_text = ""
                Column_controls[2].controls[0].disabled = False
            e.update()
            Column_controls[2].controls[0].update()

        def update_version_UI_list(e):
            self.main_page.controls[1].content.controls[1].controls = [version.control for version in self.version_list.values()]
            self.main_page.controls[1].content.controls[1].update()

        self.update_version_UI_list = update_version_UI_list

        def add_version(e):
            Column_controls = self.version_add_dialog.actions[0].content.controls
            path = Column_controls[0].controls[0].value
            if not os.path.isdir(path):
                return
            name = Column_controls[1].value
            self.version_list.update({name: rpy_version(path, name, self), })
            self.version_list = {k: self.version_list[k] for k in sorted(self.version_list, reverse=True)}
            update_version_UI_list(None)
            close_version_add_dialog(None)
            Column_controls[0].controls[0].value = Column_controls[1].value = ''

            self.app_config["default_versions"] = {}
            for version_name, version_obj in self.version_list.items():
                self.app_config["default_versions"].update({version_name: version_obj.folder_path})
            self.save_app_config()

        def close_version_add_dialog(e):
            self.version_add_dialog.open = False
            self.version_add_dialog.update()

        self.page.overlay.append(self.file_picker)
        # version文件夹选择dialog
        self.version_add_dialog = ft.AlertDialog(
            title=ft.Text("选择rpy文件所在的文件夹", size=20),
            actions=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.TextField(
                                        label="文件夹路径",
                                        width=450
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
                                on_change=version_name_check
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("添加", icon=ft.icons.CHECK, on_click=add_version),
                                    ft.TextButton("取消", icon=ft.icons.CANCEL, icon_color="#ba1a1a", on_click=close_version_add_dialog)
                                ]
                            )
                        ]
                    ),
                    height=300,
                    width=500,
                )
            ]
        )

        self.version_delete_dialog = ft.AlertDialog(
            title=ft.Text("从列表中删除version", size=20),
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            [],
                            width=400,
                            height=250,
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        ft.TextButton(
                            icon=ft.icons.CHECK_ROUNDED,
                            text="确认删除",
                            on_click=self.delete_dialog
                        )
                    ]
                )
            ]
        )

        self.add_task_dialog = ft.AlertDialog(
            title=ft.Text("新建任务", size=20),
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
                                                ft.TextButton("添加", icon=ft.icons.CHECK, on_click=self.add_modify_task),
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
                                                        ft.TextButton("计算", icon=ft.icons.LIGHTBULB, icon_color="#ff453a", on_click=self.update_task_info),
                                                        ft.TextButton("添加", icon=ft.icons.CHECK, on_click=self.add_update_task),

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

        self.transfer_dialog = ft.AlertDialog(
            title=ft.Text("转移翻译", size=20),
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            height=450,
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        ft.TextButton(
                            icon=ft.icons.CHECK_ROUNDED,
                            text="转移翻译到json",
                            on_click=self.move_task_result_to_json_file
                        )
                    ],
                    height=500,
                    width=600,
                ),
            ]
        )

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
                            on_click=self.open_setting_config
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
                            on_click=lambda _: self.page.window_close()
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
                                # icon_color="#83EBAC",
                                icon_color="#a7a7a7",
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                    }
                                ),
                                offset=(0, 1),
                                tooltip="对比 哈哈 还没做",
                                disabled=True
                                # TODO: 对比
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
                                tooltip="刷新 哈哈 摆了",
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
                                        ft.PopupMenuItem(icon=ft.icons.SAVE_AS_ROUNDED, text="另存为"),
                                        # TODO: 另存为
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
                                        ft.FilePicker()
                                    ],
                                    content=ft.Icon(
                                        name=ft.icons.MENU_ROUNDED,
                                        size=30,
                                        color="#409bdc",
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
                                    width=120,
                                    color="white",
                                    on_change=self.task_filter,
                                    hint_text="检索",
                                    hint_style=ft.TextStyle(color="#409BDC")
                                ),
                                ft.IconButton(
                                    icon=ft.icons.CABLE,
                                    icon_size=22,
                                    icon_color="#409bdc",
                                    style=ft.ButtonStyle(
                                        shape={
                                            ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                        }
                                    ),
                                    on_click=self.open_transfer,
                                    tooltip="提交任务"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ADD_ROUNDED,
                                    icon_size=22,
                                    icon_color="#409bdc",
                                    style=ft.ButtonStyle(
                                        shape={
                                            ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0),
                                        }
                                    ),
                                    on_click=self.open_add_task,
                                    tooltip="添加任务"
                                )
                            ],
                            width=200,
                            height=50,
                            spacing=0,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
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

    def open_version_folder_pick(self, e):
        self.page.dialog = self.version_add_dialog
        self.version_add_dialog.open = True
        self.page.update()

    def open_delete_version_dialog(self, e):
        checkbox_Column = self.version_delete_dialog.actions[0].controls[0]
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

    def delete_dialog(self, e):
        checkbox_Column = self.version_delete_dialog.actions[0].controls[0]
        for Row in checkbox_Column.controls:
            checkbox, version_name_text, _, _ = Row.controls
            if checkbox.value:
                version_name = version_name_text.value
                del self.version_list[version_name]

        self.version_list = {k: self.version_list[k] for k in sorted(self.version_list, reverse=True)}
        self.update_version_UI_list(None)

        self.app_config["default_versions"] = {}
        for version_name, version_obj in self.version_list.items():
            self.app_config["default_versions"].update({version_name: version_obj.folder_path})
        self.save_app_config()

        self.version_delete_dialog.open = False
        self.page.update()

    def open_add_task(self, e):
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

    def update_event_dropdown(self, e):
        rpy_file_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[1]
        event_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[2]
        selected_rpy_file = rpy_file_dropdown.value
        event_dropdown.options = [ft.dropdown.Option(event_name) for event_name in self.version_list[self.selected_version].rpy_dict[selected_rpy_file].file_json['dialogue'].keys()]
        event_dropdown.options.append(ft.dropdown.Option("strings"))
        event_dropdown.update()

    def update_dialogue_dropdown(self, e):
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

    # def add_version(self, dir_path: str, version: str):
    #     rpy_v_obj = rpy_version(dir_path, version)
    #     self.version_list.update({version: {'dir_path': dir_path, 'rpy': rpy_v_obj}})

    def check_task_description(self, e):
        task_description_textfield = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls[4]
        if task_description_textfield.value.find("@") != -1:
            task_description_textfield.error_text = "不要包含@"
        else:
            task_description_textfield.error_text = ""
        task_description_textfield.update()

    def add_modify_task(self, e):
        add_modify_task_3_dropdown = self.add_task_dialog.actions[0].content.controls[0].tabs[0].content.controls
        rpy_file_name = add_modify_task_3_dropdown[1].value
        event_name = add_modify_task_3_dropdown[2].value
        dialogue_name = add_modify_task_3_dropdown[3].value[:8]
        description = add_modify_task_3_dropdown[4].value

        if not all([rpy_file_name, event_name, dialogue_name, description]):
            return

        host_date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
        task_hex = hashlib.md5(f"{rpy_file_name}{event_name}{dialogue_name}{description}{host_date}".encode(encoding='UTF-8')).hexdigest()
        task_hex = task_hex[:8]

        task = {
            "host_name": self.user_name,
            "host_date": host_date,
            "worker_name": "",
            "last_change_data": "",
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
        for version_obj in self.version_list.values():
            version_obj.update_control()
        self.update_version_UI_list(None)

        task_column = self.main_page.controls[2].controls[1].content.content.controls[1]
        task_column.controls = [task_obj.control for task_obj in tasks_dick.values()]
        task_column.update()

        self.add_task_dialog.open = False
        self.add_task_dialog.update()

    def add_update_task(self, e):
        """
        按下按钮后添加更新任务
        :param e:
        :return:
        """

        tasks_dick = self.version_list[self.selected_version].tasks_dict

        task_info = self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[4].value

        if task_info is None:
            return
        task_info: str
        new_file, new_event, modify_line, new_or_modify_string = task_info.split("%")

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
                    "last_change_data": "",
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
                    "last_change_data": "",
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
                "last_change_data": "",
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
                "last_change_data": "",
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

    def update_task_info(self, e):
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
        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[4].value = "%".join([f"{new_file}", f"{new_event}", f"{change_line}", f"{modify_or_new_strings}"])
        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[3].controls[0].update()
        self.add_task_dialog.actions[0].content.controls[0].tabs[1].content.controls[4].update()

    def save_app_config(self):
        with open('assets/app_config.json', mode='w', encoding='utf-8') as F:
            F.write(json.dumps(self.app_config, indent=2, ensure_ascii=False))

    def rpy_file_filter(self, e):
        text_filter = e.control.value.lower()
        controls = self.main_page.controls[2].controls[0].content.content.controls[1].controls
        for rpy_file_control in controls:
            rpy_file_control.visible = False if (rpy_file_control.content.content.controls[0]).value.lower().find(text_filter) == -1 else True
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
            self.version_list.update({name: rpy_version(path, name, self)})
            self.update_version_UI_list(None)

    def open_setting_config(self, e):
        self.setting_config_dialog.actions[0].content.controls[0].controls[1].value = self.app_config["user_name"]
        self.setting_config_dialog.actions[0].content.controls[1].controls[1].value = str(self.app_config["task_auto_save"])
        self.setting_config_dialog.actions[0].content.controls[2].controls[1].value = str(self.app_config["game_path"])
        self.setting_config_dialog.actions[0].content.controls[3].controls[1].value = str(self.app_config["appid"])
        self.setting_config_dialog.actions[0].content.controls[4].controls[1].value = str(self.app_config["appkey"])
        self.page.dialog = self.setting_config_dialog
        self.setting_config_dialog.open = True
        self.page.update()

    def open_transfer(self, e):
        if self.selected_version == "":
            return
        rpy_dict = self.version_list[self.selected_version].rpy_dict
        transfer_Column = self.transfer_dialog.actions[0].controls[0]
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

            acc = len([tl for _, _, tl in task.task_result.values() if tl != ""]) / acc

            description: str = task.description

            label = description.ljust(50) + str(int(acc * 10000) / 100).rjust(5) + "%"
            transfer_Column.controls.append(
                ft.Row(
                    [
                        ft.Checkbox(
                            value=acc == 1
                        ),
                        ft.Text(task_hex, visible=False),
                        ft.Text(
                            value=description,
                            font_family="Consolas",
                            size=15,
                            width=400,
                        ),
                        ft.Text(
                            value=str(int(acc * 10000) / 100).rjust(5) + "%",
                            font_family="Consolas",
                            size=15,
                            width=60,
                            color="#FF0000" if acc == 1 else ""
                        ),
                    ]
                )

            )

        self.page.dialog = self.transfer_dialog
        self.transfer_dialog.open = True
        self.page.update()

    def move_task_result_to_json_file(self, e):
        check_boxes_column = self.transfer_dialog.actions[0].controls[0]
        ver_obj = self.version_list[self.selected_version]
        update_rpy_set = set()
        for row in check_boxes_column.controls:
            checkbox, task_hex, _, _ = row.controls
            if checkbox.value:
                task_obj = self.version_list[self.selected_version].tasks_dict[task_hex.value]
                for dialogue, (file_name, event_name, translation) in task_obj.task_result.items():
                    update_rpy_set.add(file_name)
                    if event_name == "strings":
                        for strings_list in ver_obj.rpy_dict[file_name].file_json["strings"]:
                            for strings in strings_list:
                                if hashlib.md5(strings["old"].encode("utf-8")).hexdigest()[:8] == dialogue:
                                    strings["new"] = translation
                    else:
                        ver_obj.rpy_dict[file_name].file_json["dialogue"][event_name][dialogue]["translation"] = translation

        for file_name in update_rpy_set:
            rpy_obj = ver_obj.rpy_dict[file_name]
            rpy_obj.json_info_value = ""
            rpy_obj.rpy_info_value = ""
            rpy_obj.line_num = {
                "rpy": 0,
                "json": 0
            }
            rpy_obj.showing_type = ""
            rpy_obj.write_json(os.path.join(self.version_list[self.selected_version].folder_path))

        self.transfer_dialog.open = False
        self.page.update()

    def save_setting_config(self, e):
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