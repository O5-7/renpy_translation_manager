import csv
import json

import os
import threading
import time

import flet as ft
from renpy_tool import *

info = list("word,phonetic,definition,translation,pos,collins,oxford,tag,bnc,frq,exchange,detail,audio".split(","))


class En_dict:
    def __init__(self, rm):
        super().__init__()
        self.Rm = rm
        if os.path.isfile("assets/ecdict.csv") and os.path.isfile("assets/dict_line.json"):
            self.dict_json = json.load(open("assets/dict_line.json", encoding="utf-8"))

        self.is_auto_save_on = False
        self.count = 0
        self.auto_save_th = threading.Thread(
            target=auto_save_threading,
            args=[self],
            daemon=True
        )
        self.control = self.build_control()

    def En_dict(self, _):
        En_input = self.control.content.controls[0].value.lower()
        running_log(f"查询字典 {En_input}")
        en_description = self.control.content.controls[1].controls[2]
        cn_description = self.control.content.controls[1].controls[0]
        if En_input not in self.dict_json.keys():
            en_description.value = "查询失败"
            cn_description.value = ""
            en_description.update()
            cn_description.update()
            running_log(f"查询失败")
            return
        line_num = self.dict_json[En_input] + 1
        with open("assets/ecdict.csv", mode="r", encoding="utf-8") as F:
            for _ in range(line_num):
                F.readline()
            word_line = csv.reader(F, delimiter=',').__next__()
            en_description.value = word_line[2].replace("\\n", "\n\n")
            cn_description.value = word_line[3].replace("\\n", "\n\n")
            en_description.update()
            cn_description.update()
            running_log(f"查询成功")

    def build_control(self):
        out_control = ft.Container(
            content=ft.Column(
                [
                    ft.TextField(
                        height=50,
                        width=160,
                        border=ft.InputBorder.UNDERLINE,
                        filled=True,
                        multiline=False,
                        text_size=17,
                        on_submit=self.En_dict,
                        hint_text="字典",
                        disabled=not (os.path.isfile("assets/ecdict.csv") and os.path.isfile("assets/dict_line.json"))
                    ),
                    ft.Column(
                        [
                            ft.Text(width=160, selectable=True, font_family="Hans"),
                            ft.Divider(),
                            ft.Text(width=160, selectable=True, font_family="Hans"),
                        ],
                        spacing=0,
                        scroll=ft.ScrollMode.ALWAYS,
                        height=727,
                    ),
                    ft.TextButton(
                        height=75,
                        width=150,
                        content=ft.Text(
                            value="保存到文件",
                            font_family="Hans",
                            size=20,
                            color="#FF7F00"
                        ),
                        style=ft.ButtonStyle(
                            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=5)},
                            bgcolor="#FFFFFF",
                            side={ft.MaterialState.DEFAULT: ft.BorderSide(5, "#FF7F00")},
                            color="#FF7F00"
                        ),
                        on_click=self.save_to_file,
                    ),
                    ft.ProgressBar(
                        value=0,
                        width=150,
                        height=20,
                        color="#FF7F00",
                        tooltip="自动保存倒计时",
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            bgcolor="#eeeeee",
            border_radius=0,
            border=ft.border.all(2, "#000000")
        )

        return out_control

    def save_to_file(self, _):
        running_log(f"尝试保存任务")
        if not self.is_auto_save_on:
            self.is_auto_save_on = True
            self.auto_save_th.start()
        tasks_dict = self.Rm.version_list[self.Rm.selected_version].tasks_dict
        task = tasks_dict[self.Rm.selected_task]
        if task.worker_name == "":
            task.worker_name = self.Rm.user_name
            task.control = task.build_control()
            task_column = self.Rm.main_page.controls[2].controls[1].content.content.controls[1]
            task_column.controls = [task_obj.control for task_obj in tasks_dict.values()]
            for c in task_column.controls:
                c.visible = True
            task_column.update()

        running_log(f"保存任务 {self.Rm.selected_version} >>> {task.description} 到本地")
        task.write()


def auto_save_threading(self):
    pb = self.Rm.main_page.controls[3].content.controls[2].controls[0].content.controls[3]

    while True:
        pb.value = self.count / self.Rm.app_config["task_auto_save"]
        try:
            pb.update()
        except AssertionError:
            return
        time.sleep(0.2)
        self.count += 0.2
        if self.count >= self.Rm.app_config["task_auto_save"]:
            task = self.Rm.version_list[self.Rm.selected_version].tasks_dict[self.Rm.selected_task]
            task.write()
            self.count = 0
