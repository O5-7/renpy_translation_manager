import random
import re

import flet as ft
import os
import json
import hashlib
import requests

name_dict = json.load(open("assets/name_color.json", mode="r", encoding="utf-8"))


class text_editor:
    def __init__(self, file_name: str, event_name: str, dialogue: str, task_obj, rm):
        super().__init__()
        self.hint = ""
        self.origin = ""
        self.script = ""
        self.speaker = ""
        self.speaker_color = ""
        self.file_name = file_name
        self.event_name = event_name
        self.dialogue = dialogue
        self.task_obj = task_obj
        self.Rm = rm
        self.control = self.build_control()
        if dialogue in task_obj.task_result.keys():
            self.control.content.controls[3].controls[0].value = task_obj.task_result[dialogue][2]

    def build_control(self):
        rpy_dict = self.Rm.version_list[self.Rm.selected_version].rpy_dict
        rpy_obj = rpy_dict[self.file_name]
        if self.event_name == "strings":
            for strings_list in rpy_obj.file_json["strings"]:
                for strings in strings_list:
                    if hashlib.md5(strings["old"].encode(encoding='UTF-8')).hexdigest()[:8] == self.dialogue:
                        self.origin = strings["old"]
                        self.hint = strings["new"]
                        self.script = strings["script"]
        else:
            tr_dict = rpy_obj.file_json["dialogue"][self.event_name][self.dialogue]
            self.speaker = "" if tr_dict["speaker"] == "<>" else name_dict[tr_dict["speaker"]][0]
            self.speaker_color = "" if tr_dict["speaker"] == "<>" else name_dict[tr_dict["speaker"]][1]
            self.origin = tr_dict["origin"]
            self.hint = tr_dict["translation"]
            self.script = tr_dict["script"]

        control = ft.Container(
            ft.Column(
                [
                    ft.Text(self.speaker, color=self.speaker_color, font_family="Consolas", size=20, ),
                    ft.Text(self.origin, font_family="Consolas", size=20, selectable=True),
                    ft.Text(self.hint, font_family="黑体", size=17, selectable=True, color="#878787"),
                    ft.Row(
                        [
                            ft.TextField(
                                width=752,
                                on_change=self.update_in_memory,
                                text_size=17,
                                border=ft.InputBorder.UNDERLINE,
                                filled=True,
                                multiline=True,
                                border_radius=0,
                            ),
                            ft.IconButton(
                                icon=ft.icons.RAW_ON_ROUNDED,
                                style=ft.ButtonStyle(
                                    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0)},
                                    side={ft.MaterialState.DEFAULT: ft.BorderSide(1, "#000000")},
                                ),
                                icon_size=33,
                                on_click=self.open_in_script,
                                tooltip="原地址",
                            ),
                            ft.IconButton(
                                icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
                                style=ft.ButtonStyle(
                                    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0)},
                                    side={ft.MaterialState.DEFAULT: ft.BorderSide(1, "#000000")},
                                ),
                                icon_size=33,
                                on_click=self.transfer,
                                tooltip="复制提示翻译",
                            ),
                            ft.IconButton(
                                icon=ft.icons.TRANSLATE_ROUNDED,
                                style=ft.ButtonStyle(
                                    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0)},
                                    side={ft.MaterialState.DEFAULT: ft.BorderSide(1, "#000000")},
                                ),
                                icon_size=33,
                                on_click=self.translate_self,
                                tooltip="在线翻译",
                            )
                        ],
                        spacing=0
                    ),
                    ft.Text(self.script, visible=False)
                ],
                spacing=1
            ),
            bgcolor="#eeeeee",
            width=1050,
        )

        return control

    def translate_self(self, e):

        query = self.control.content.controls[1].value
        target = ""

        free_target = self.translate_free(query)
        if "target" in free_target.keys():
            target = free_target["target"]
        else:
            cost_target = self.translate_cost(query)
            if "trans_result" in cost_target.keys():
                target = cost_target["trans_result"][0]["dst"]
            else:
                target = "错误"

        self.control.content.controls[3].controls[0].value = target
        self.control.content.controls[3].controls[0].update()
        self.update_in_memory(None)

    def transfer(self, e):
        if self.hint == "":
            return
        self.control.content.controls[3].controls[0].value = self.hint
        self.control.content.controls[3].controls[0].update()
        self.update_in_memory(None)

    def open_in_script(self, e):
        line_cut_index = self.script.rfind(":")
        file_path = os.path.join(self.Rm.app_config["game_path"], self.script[:line_cut_index])
        line_num = self.script[line_cut_index + 1:]
        cmd = f"notepad.exe /g {line_num} {file_path}"
        os.system(cmd)

    def update_in_memory(self, e):
        new_translation = self.control.content.controls[3].controls[0].value
        self.task_obj.task_result.update({self.dialogue: [self.file_name, self.event_name, new_translation]})

    def translate_cost(self, query):
        appid = self.Rm.app_config["appid"]
        appkey = self.Rm.app_config["appkey"]

        if appid == "" or appkey == "":
            return {}

        from_lang = 'auto'
        to_lang = 'zh'

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path

        query = query.replace('{i}', '').replace('{/i}', '')
        query = query.replace('{b}', '').replace('{/b}', '')
        query = query.replace('{s}', '').replace('{/s}', '')
        query = re.sub(r'{size=[-+]?\d+}', '', query).replace('{/size}', '')

        salt = random.randint(32768, 65536)
        sign = hashlib.md5((appid + query + str(salt) + appkey).encode("utf-8")).hexdigest()

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        r = requests.post(url, params=payload, headers=headers)
        target = r.json()
        return target

    def translate_free(self, query):
        url = "http://api.interpreter.caiyunai.com/v1/translator"

        token = "3975l6lr5pcbvidl6jl2"

        payload = {
            "source": query,
            "trans_type": "auto2zh",
            "request_id": "demo",
            "detect": True,
        }

        headers = {
            "content-type": "application/json",
            "x-authorization": "token " + token,
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        return json.loads(response.text)