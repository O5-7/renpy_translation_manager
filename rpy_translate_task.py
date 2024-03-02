import hashlib
import time

import flet as ft
import os
import json
import datetime
from text_editor import text_editor
from English_dict import En_dict

date_format = '%Y-%m-%d %H:%M:%S'


class rpy_translation_task:
    def __init__(self, file_path: str, rm):
        self.Rm = rm

        self.file_path = file_path
        self.host_name: str = ''
        self.host_date: str = ''
        self.worker_name: str = ''
        self.last_change_data: str = ''
        self.hex: str = ''
        self.description: str = ''
        self.task_type: str = ''  # ["update, ""modify"]
        self.task_content: dict = {}
        self.task_result: dict = {}

        self.acc = 0

        with open(file_path, mode='r', encoding='utf-8') as F:
            read_json = json.load(F)
            self.host_name = read_json['host_name']
            self.host_date = read_json['host_date']
            self.worker_name = read_json['worker_name']
            self.last_change_data = read_json['last_change_data']
            self.hex = read_json['hex']
            self.description = read_json['description']
            self.task_type = read_json['task_type']
            self.task_content = read_json['task_content']
            self.task_result = read_json['task_result']

        self.control = self.build_control()

    def update_control(self):
        self.control = self.build_control()

    def build_control(self):
        rpy_task_control = ft.GestureDetector(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"{self.description}", size=10),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    height=30,
                ),
                width=200,
                border=ft.border.all(5, color="#618aeb" if self.task_type == "modify" else "#656feb"),
                border_radius=5,
                bgcolor="#8ab6de" if self.task_type == "modify" else "#90aade",
            ),
            on_double_tap=self.show_task_editor,
            on_enter=self.enter_task,
            on_exit=self.exit_task,
            animate_size=100,
        )

        return rpy_task_control

    def read(self):
        with open(self.file_path, mode='r', encoding='utf-8') as F:
            read_json = json.load(F)
            self.host_name = read_json['host_name']
            self.host_date = read_json['host_date']
            self.worker_name = read_json['worker_name']
            self.last_change_data = read_json['last_change_data']
            self.hex = read_json['hex']
            self.description = read_json['description']
            self.task_type = read_json['task_type']
            self.task_content = read_json['task_content']
            self.task_result = read_json['task_result']

        self.control = self.build_control()

    def write(self):
        # print(f"write {self.description}")
        with open(self.file_path, mode='w', encoding='utf-8') as F:
            task_json = {
                "host_name": self.host_name,
                "host_date": self.host_date,
                "worker_name": self.worker_name,
                "last_change_data": datetime.datetime.fromtimestamp(time.time()).strftime(date_format),
                "hex": self.hex,
                "task_type": self.task_type,
                "description": self.description,
                "task_content": self.task_content,
                "task_result": self.task_result
            }
            F.write(json.dumps(task_json, indent=2, ensure_ascii=False))

    def show_task_editor(self, e):
        self.Rm.selected_task = self.hex
        self.Rm.page.controls[0].controls[1].content.content.value = f"RPY Manager >>> {self.Rm.selected_version} >> {self.description}"
        self.Rm.page.controls[0].controls[1].content.content.update()

        rpy_dict = self.Rm.version_list[self.Rm.selected_version].rpy_dict
        text_con = self.Rm.main_page.controls[3]

        text_con.content = ft.Row(
            [
                ft.Container(),
                ft.Column(
                    spacing=0,
                    scroll=ft.ScrollMode.ALWAYS,
                    height=890,
                    width=900,
                ),
                ft.Column(
                    [
                        En_dict(self.Rm).control
                    ],
                    height=890,
                    spacing=0
                )
            ],
            height=890,
            spacing=0
        )

        for file_name, event_dict in self.task_content.items():
            rpy_file = rpy_dict[file_name]
            for event_name, dialogues in event_dict.items():
                if event_name == "strings":
                    if dialogues[0] == "ALL":
                        for strings in rpy_file.file_json["strings"]:
                            for string in strings:
                                dialogue = hashlib.md5(string["old"].encode(encoding='UTF-8')).hexdigest()[:8]
                                text_con.content.controls[1].controls.append(
                                    text_editor(file_name, "strings", dialogue, self, self.Rm).control
                                )
                    else:
                        for dialogue in dialogues:
                            text_con.content.controls[1].controls.append(
                                text_editor(file_name, "strings", dialogue[:8], self, self.Rm).control
                            )
                else:
                    if dialogues[0] == "ALL":
                        for dialogue in rpy_file.file_json["dialogue"][event_name].keys():
                            text_con.content.controls[1].controls.append(
                                text_editor(file_name, event_name, dialogue, self, self.Rm).control
                            )
                    else:
                        for dialogue in dialogues:
                            text_con.content.controls[1].controls.append(
                                text_editor(file_name, event_name, dialogue, self, self.Rm).control
                            )

        text_con.update()

    def enter_task(self, e):
        task_column = self.Rm.main_page.controls[2].controls[1].content.content.controls[1]
        for task in task_column.controls:
            if len(task.content.content.controls) != 1:
                continue
            text = task.content.content.controls[0].value
            if text == self.description:
                task.content.content = ft.Column(
                    [
                        ft.Text(f" 发布: {self.host_name}"),
                        ft.Text(f" 翻译: {self.worker_name}"),
                        ft.Text(f" 类型: {self.task_type}"),
                        ft.Text(f" 描述: {self.description}"),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    height=120,
                )
                task_column.update()
                return

    def exit_task(self, e):
        task_column = self.Rm.main_page.controls[2].controls[1].content.content.controls[1]
        for task in task_column.controls:
            if len(task.content.content.controls) != 4:
                continue
            text = task.content.content.controls[3].value
            if text[5:] == self.description:
                task.content.content = ft.Column(
                    [
                        ft.Text(f"{self.description}", size=10),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    animate_size=500,
                    height=30,
                )
                task_column.update()
                return
