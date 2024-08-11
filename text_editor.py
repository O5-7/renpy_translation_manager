import random
import re
from nltk import Tree
import flet as ft
import os
import json
import hashlib
import requests
from difflib import Differ

from renpy_tool import *

flag_color_dict = {
    "-": "#daa7a7",
    "+": "#a7daa7",
    " ": "#eeeeee",
    "?": "#a7a7da"
}


class text_editor:
    def __init__(self, file_name: str, event_name: str, dialogue: str, task_obj, rm):
        super().__init__()
        self.hint = ""
        self.origin = ""
        self.no_flag_origin = ""
        self.script = ""
        self.speaker = ""
        self.speaker_color = ""
        self.file_name = file_name
        self.event_name = event_name
        self.dialogue = dialogue
        self.task_obj = task_obj
        self.Rm = rm
        self.control = self.build_control()
        self.is_syntax_tree = False
        self.sents_depth_list = []

        try:
            # 读取保存在内存的翻译
            new_translation = task_obj.task_result[self.file_name][self.event_name][self.dialogue]
            self.control.content.controls[3].controls[0].value = new_translation
            self.control.content.controls[3].controls[0].bgcolor = "#dfe2eb"

            hint_text = self.control.content.controls[2]
            if new_translation:
                hint_text.value = ""
                hint_text.spans = []
                diff_result = Differ().compare(self.hint, new_translation)
                temp_flag = '%'
                for res in diff_result:
                    flag = res[0]
                    word = res[2]
                    if flag == temp_flag:
                        hint_text.spans[-1].text += word
                    else:
                        temp_flag = flag
                        hint_text.spans.append(
                            ft.TextSpan(
                                word,
                                ft.TextStyle(
                                    # color=flag_color_dict[flag],
                                    decoration=ft.TextDecoration.UNDERLINE if flag != " " else None,
                                    decoration_color=flag_color_dict[flag],
                                    bgcolor=flag_color_dict[flag]
                                )
                            )
                        )
            else:
                hint_text.value = self.hint
                hint_text.spans = []
                hint_text.update()

        except KeyError:
            pass

        self.syntax_tree_dialog = ft.AlertDialog(
            title=ft.Text("依存句法分析", size=20),
            actions=[
                ft.Container(
                    width=1000,
                    height=600,
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=0,
                        tabs=[],
                    )
                )
            ]
        )

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

            self.speaker = self.Rm.name_dict[tr_dict["speaker"]][0] if tr_dict["speaker"] in self.Rm.name_dict.keys() else f"{tr_dict['speaker']} <未知的角色 请检查设置中的游戏根目录>"
            self.speaker_color = self.Rm.name_dict[tr_dict["speaker"]][1] if tr_dict["speaker"] in self.Rm.name_dict.keys() else ""
            if tr_dict["speaker"] == "<>":
                self.speaker = ""

            self.origin = tr_dict["origin"]
            self.hint = tr_dict["translation"]
            self.script = tr_dict["script"]

        control = ft.Container(
            ft.Column(
                [
                    ft.Text(self.speaker, color=self.speaker_color, font_family="黑体", size=20, ),
                    ft.Text(self.origin, font_family="Hans", size=20, selectable=True),
                    ft.Text(self.hint, font_family="Hans", size=18, selectable=True, color="#5f5f5f"),
                    ft.Row(
                        [
                            ft.TextField(
                                width=700,
                                on_change=self.update_in_memory,
                                text_size=17,
                                border=ft.InputBorder.UNDERLINE,
                                filled=True,
                                multiline=True,
                                border_radius=0,
                                bgcolor="#eb969f"
                            ),
                            ft.IconButton(
                                icon=ft.icons.ANALYTICS_ROUNDED,
                                style=ft.ButtonStyle(
                                    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0)},
                                    side={ft.MaterialState.DEFAULT: ft.BorderSide(1, "#000000")},
                                ),
                                icon_size=33,
                                on_click=self.show_syntax_tree_dialog,
                                tooltip="句法树解析",
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

        self.no_flag_origin = self.origin
        self.no_flag_origin = self.no_flag_origin.replace('{i}', '').replace('{/i}', '')
        self.no_flag_origin = self.no_flag_origin.replace('{b}', '').replace('{/b}', '')
        self.no_flag_origin = self.no_flag_origin.replace('{s}', '').replace('{/s}', '')
        self.no_flag_origin = re.sub(r'{size=[-+]?\d+}', '', self.no_flag_origin).replace('{/size}', '')


        return control

    def translate_self(self, _):
        running_log(f"在线翻译 {self.origin[:20]}")
        target = ""

        free_target = self.translate_free(self.no_flag_origin)
        if "target" in free_target.keys():
            target = free_target["target"]
        else:
            cost_target = self.translate_cost(self.no_flag_origin)
            if "trans_result" in cost_target.keys():
                target = cost_target["trans_result"][0]["dst"]
            else:
                target = "错误 请检查appid和appkey"

        self.control.content.controls[3].controls[0].value = target
        self.control.content.controls[3].controls[0].update()
        self.update_in_memory(None)

    def transfer(self, _):
        if self.hint == "":
            return
        self.control.content.controls[3].controls[0].value = self.hint
        self.control.content.controls[3].controls[0].update()
        self.update_in_memory(None)

    def open_in_script(self, _):
        if self.Rm.app_config["game_path"] == "":
            return
        line_cut_index = self.script.rfind(":")
        file_path = os.path.join(self.Rm.app_config["game_path"], self.script[:line_cut_index])
        line_num = self.script[line_cut_index + 1:]
        cmd = f"notepad.exe /g {line_num} {file_path}"
        os.system(cmd)

    def update_in_memory(self, _):
        new_translation = self.control.content.controls[3].controls[0].value

        text_field = self.control.content.controls[3].controls[0]
        text_field.bgcolor = "#eb969f" if new_translation == "" else "#dfe2eb"
        text_field.update()

        if self.hint:
            hint_text: ft.Text
            hint_text = self.control.content.controls[2]
            if new_translation:
                hint_text.value = ""
                hint_text.spans = []
                diff_result = Differ().compare(self.hint, new_translation)
                temp_flag = '%'
                for res in diff_result:
                    flag = res[0]
                    word = res[2]
                    if flag == temp_flag:
                        hint_text.spans[-1].text += word
                    else:
                        temp_flag = flag
                        hint_text.spans.append(
                            ft.TextSpan(
                                word,
                                ft.TextStyle(
                                    # color=flag_color_dict[flag],
                                    decoration=ft.TextDecoration.UNDERLINE if flag != " " else None,
                                    decoration_color=flag_color_dict[flag],
                                    bgcolor=flag_color_dict[flag],
                                )
                            )
                        )
            else:
                hint_text.value = self.hint
                hint_text.spans = []
            hint_text.update()

        # self.task_obj.task_result.update({self.dialogue: [self.file_name, self.event_name, new_translation]}) # 可能会有歧义冲突
        if self.file_name not in self.task_obj.task_result.keys():
            self.task_obj.task_result.update({self.file_name: {}})
        if self.event_name not in self.task_obj.task_result[self.file_name].keys():
            self.task_obj.task_result[self.file_name].update({self.event_name: {}})
        if self.dialogue not in self.task_obj.task_result[self.file_name][self.event_name].keys():
            self.task_obj.task_result[self.file_name][self.event_name].update({self.dialogue: ""})

        self.task_obj.task_result[self.file_name][self.event_name].update({self.dialogue: new_translation})

    def translate_cost(self, query):
        running_log(f"百度翻译")
        appid = self.Rm.app_config["appid"]
        appkey = self.Rm.app_config["appkey"]

        if appid == "" or appkey == "":
            return {}

        from_lang = 'auto'
        to_lang = 'zh'

        endpoint = 'https://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path

        salt = random.randint(32768, 65536)
        sign = hashlib.md5((appid + query + str(salt) + appkey).encode("utf-8")).hexdigest()

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        r = requests.post(url, params=payload, headers=headers)
        target = r.json()
        return target

    def translate_free(self, query):
        running_log(f"彩云翻译")
        url = "https://api.interpreter.caiyunai.com/v1/translator"

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

    def show_syntax_tree_dialog(self, _):
        if not self.is_syntax_tree:
            def to_nltk_tree(node):
                if node.n_lefts + node.n_rights > 0:
                    return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
                else:
                    return node.orth_

            def rebuild(node: Tree, depth: int = 0):
                out = [[node.label(), depth]]
                for n in node:
                    if type(n) == str:
                        out.append([n, depth])
                    else:
                        out += rebuild(n, depth + 1)
                return out

            doc = self.Rm.nlp(self.no_flag_origin)

            origin = [token.text for token in doc]
            for sent in doc.sents:
                depth_l = rebuild(to_nltk_tree(sent.root))
                out_list = [(world, -1) for world in origin[:len(depth_l)]]

                for world, depth in depth_l:
                    for num, (world_o, depth_o) in enumerate(out_list):
                        if depth_o > -1:
                            continue
                        if world == world_o:
                            out_list[num] = (world, depth)
                            break
                self.sents_depth_list.append(out_list)
                origin = origin[len(depth_l):]
            tabs_list = self.syntax_tree_dialog.actions[0].content.tabs
            for num, sent_depth in enumerate(self.sents_depth_list):
                tab = ft.Tab(
                    text=f"第{num + 1}句",
                    content=ft.Column(
                        [
                            ft.Slider(min=0, max=10, divisions=10, label="深度={value}", value=0, on_change=self.depth_change),
                            ft.Row(
                                width=980,
                                height=470,
                                scroll=ft.ScrollMode.ALWAYS,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                spacing=0,
                            )
                        ]
                    )
                )
                row_list = tab.content.controls[1].controls
                for world, depth in sent_depth:
                    row_list.append(
                        ft.Column(
                            [
                                ft.Container(
                                    height=40 * depth,
                                    width=3,
                                    bgcolor="#e0e0e0",
                                    animate_size=200,
                                ),
                                ft.Container(
                                    ft.Text(world + ' ', size=35, ),
                                    border_radius=1,
                                ),
                                ft.Container(height=10)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            spacing=0)
                    )
                tabs_list.append(tab)

        self.is_syntax_tree = True
        self.Rm.page.dialog = self.syntax_tree_dialog
        self.syntax_tree_dialog.open = True
        self.Rm.page.update()

    def depth_change(self, e):
        value = int(e.control.value)
        sent_index = self.syntax_tree_dialog.actions[0].content.selected_index
        tab_s = self.syntax_tree_dialog.actions[0].content.tabs[sent_index]
        for i in range(len(self.sents_depth_list[sent_index])):
            tab_s.content.controls[1].controls[i].controls[0].height = 40 * min(self.sents_depth_list[sent_index][i][1], value)
        tab_s.update()
