import os
import json
import flet as ft
from running_log import running_log

line_height = 21


class RPY_File:
    def __init__(self, path: str, Rm):
        self.Rm = Rm
        self.file_path = path

        type_i = os.path.basename(path).rfind('.')
        self.file_name = os.path.basename(path)[:type_i]
        self.file_type = os.path.basename(path)[type_i + 1:]

        self.json_info_value = ""
        self.rpy_info_value = ""
        self.line_num = {
            "rpy": 0,
            "json": 0
        }
        self.showing_type = ""

        self.file_json = {
            'name': self.file_name,
            "language": '',
            'dialogue': {},
            'strings': []
        }

        if self.file_type == 'rpy':
            self.read_rpy()
        elif self.file_type == 'json':
            self.read_json()
        else:
            print('not_support_file')
            return

        self.control = self.build_control()

    def update_control(self):
        self.control = self.build_control()

    def read_rpy(self):
        running_log(f"读取rpy: {self.file_name}", self.Rm)
        with open(self.file_path, mode='r', encoding='utf-8') as F:
            lines = F.readlines()
        clear_lines = []
        clear_lines_len = 0
        strings_start = -1
        # 筛选有效信息 并 找出strings的起始位置
        # dialogue_lines的长度应为4的倍数
        for line in lines:
            line: str
            if line == '\n':
                continue
            if line.startswith('﻿'):
                # 去除空字符
                line = line[1:]
            if line.startswith('#') and not line.startswith('# game/'):
                continue

            # 去除结尾换行符
            clear_lines.append(line[:-1])
            clear_lines_len += 1
            if strings_start < 0 and line.endswith('strings:\n'):
                strings_start = clear_lines_len - 1

        if strings_start == -1:
            dialogue_lines = clear_lines
            string_lines = []
        else:
            dialogue_lines = clear_lines[:strings_start]
            string_lines = clear_lines[strings_start:]

        # 对话部分
        for dialogue_index in range(len(dialogue_lines) // 4):
            script = dialogue_lines[dialogue_index * 4][2:]
            _ = dialogue_lines[dialogue_index * 4 + 1]
            _, language, event_and_hex = dialogue_lines[dialogue_index * 4 + 1].split(' ')
            event_name, dialogue_hex = event_and_hex[:-1].split('_', maxsplit=1)
            origin_line = dialogue_lines[dialogue_index * 4 + 2][5:]
            origin_start = origin_line.find('"')
            speaker = '<>' if origin_start == 1 else origin_line[1:origin_start - 1]
            origin = origin_line[origin_start + 1:-1]
            translation = dialogue_lines[dialogue_index * 4 + 3][dialogue_lines[dialogue_index * 4 + 3].find('"') + 1: -1]
            # print(script, event_name, dialogue_hex[:-1], speaker, origin, translation)

            self.file_json["language"] = language
            # dialogue装入json
            try:
                self.file_json["dialogue"][event_name].update(
                    {dialogue_hex: {
                        "script": script,
                        "speaker": speaker,
                        "origin": origin,
                        "translation": translation
                    }}
                )
            except KeyError:
                self.file_json["dialogue"].update({event_name: {}})
                self.file_json["dialogue"][event_name].update(
                    {dialogue_hex: {
                        "script": script,
                        "speaker": speaker,
                        "origin": origin,
                        "translation": translation
                    }}
                )
        # strings装入json
        string_index = 0
        while True:
            if string_index >= len(string_lines):
                break
            if string_lines[string_index].startswith("translate"):
                self.file_json["language"] = string_lines[string_index].split(' ')[1]
                self.file_json['strings'].append([])
                string_index += 1
            else:
                script = string_lines[string_index][6:]
                old = string_lines[string_index + 1][9:-1]
                new = string_lines[string_index + 2][9:-1]
                self.file_json['strings'][-1].append({
                    "script": script,
                    "old": old,
                    "new": new
                })
                string_index += 3

    def read_json(self):
        # running_log(f"读取json {self.file_name}", self.Rm)
        with open(self.file_path, mode='r', encoding='utf-8') as F:
            self.file_json = json.load(F)

    def write_json(self, folder_path: str):
        running_log(f"写json {self.file_name} 在 {folder_path}", self.Rm)
        json_str = json.dumps(self.file_json, indent=2, ensure_ascii=False)
        with open(os.path.join(folder_path, self.file_json['name'] + '.json'), mode='w', encoding='utf-8') as F:
            F.write(json_str)

    def write_rpy(self, folder_path: str):
        running_log(f"写rpy {self.file_name} 在 {folder_path}", self.Rm)
        write_str = ''
        with open(os.path.join(folder_path, self.file_json['name'] + '.rpy'), mode='w', encoding='utf-8') as F:
            for event, lines in self.file_json['dialogue'].items():
                for dialogue_hex, line in lines.items():
                    line = """# {script}\ntranslate {language} {event}_{dialogue_hex}:\n\n    # {speaker}"{origin}"\n    {speaker}"{translation}"\n\n""".format(
                        script=line['script'],
                        language=self.file_json['language'],
                        event=event,
                        dialogue_hex=dialogue_hex,
                        speaker='' if line['speaker'] == '<>' else '{} '.format(line['speaker']),
                        origin=line['origin'],
                        translation=line['translation']
                    )
                    write_str += line
            for strings in self.file_json['strings']:
                write_str += 'translate {} strings:\n\n'.format(self.file_json['language'])
                for string in strings:
                    string_str = """    # {script}\n    old "{old}"\n    new "{new}"\n\n""".format(
                        script=string['script'],
                        old=string['old'],
                        new=string['new']
                    )
                    write_str += string_str

            F.write(write_str)
        return write_str

    def build_control(self):
        rpy_file_control = ft.GestureDetector(
            content=ft.Container(
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f" {self.file_name}", size=18, ),
                                ft.Text(f" 事件:{len(self.file_json['dialogue'])}".ljust(8) + f"strings:{sum([len(strings) for strings in self.file_json['strings']])}", size=15)
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.IconButton(
                            icon=ft.icons.FILE_OPEN_SHARP,
                            style=ft.ButtonStyle(
                                shape={
                                    ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0)
                                },
                            ),
                            icon_size=30,
                            on_click=lambda _: os.system(f"notepad {self.file_path}".replace(".json", ".rpy"))
                        )
                    ],
                    width=200,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                width=200,
                height=60,
                border=ft.border.all(5, color="#8aabeb"),
                border_radius=5,
                bgcolor="#a7c2de",
                ink=True,
            ),
            on_double_tap=self.show_file_info
        )

        return rpy_file_control

    def show_file_info(self, _):
        running_log(f"打开rpy {self.file_name}", self.Rm)
        self.Rm.page.controls[0].controls[1].content.content.value = f"RTM >>> {self.Rm.selected_version} >> {self.file_name}"
        self.Rm.page.controls[0].controls[1].content.content.update()

        for file_name, file in self.Rm.version_list[self.Rm.selected_version].rpy_dict.items():
            if file_name == self.file_name:
                continue
            file.rpy_info_value = ''
            file.json_info_value = ''
        text_con = self.Rm.main_page.controls[3]
        pb = ft.ProgressBar(width=1040, color="amber", bgcolor="#eeeeee", height=20)
        text_con.content = pb
        text_con.update()
        if self.rpy_info_value == "":
            self.update_rpy_txt(pb)
        self.showing_type = "rpy"
        text_con.content = ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.TextField(
                            hint_text="行数",
                            bgcolor="#eeeeee",
                            width=100,
                            on_change=self.jump_to,
                            border_color="#FF7F00",
                        ),
                        ft.TextField(
                            bgcolor="#eeeeee"
                        ),
                        ft.IconButton(
                            icon=ft.icons.SEARCH_ROUNDED,
                            icon_size=30,
                            icon_color="#FF7F00",
                            style=ft.ButtonStyle(
                                shape={
                                    ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=0)
                                }
                            ),
                            on_click=self.text_search
                        ),
                        ft.TextButton(
                            content=ft.Text("json", size=30, offset=(0, -0.1)),
                            style=ft.ButtonStyle(
                                color="#ebb67d",
                                bgcolor="#7d5c17",
                                side={
                                    ft.MaterialState.DEFAULT: ft.BorderSide(3, "#ff7f00")
                                },
                                shape={
                                    ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=3),
                                },
                                animation_duration=150
                            ),
                            height=50,
                            width=100,
                            on_click=self.switch_to_json_info
                        ),
                        ft.TextButton(
                            content=ft.Text("rpy", size=30, offset=(0, -0.1)),
                            style=ft.ButtonStyle(
                                color="#ebb67d",
                                bgcolor="#7d5c17",
                                side={
                                    ft.MaterialState.DEFAULT: ft.BorderSide(3, "#ff7f00")
                                },
                                shape={
                                    ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=3),
                                },
                                animation_duration=150
                            ),
                            height=50,
                            width=100,
                            on_click=self.switch_to_rpy_info
                        )
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        value=self.rpy_info_value,
                                        color="#000000",
                                        size=15,
                                        font_family="黑体"
                                    ),
                                    bgcolor="#eeeeee"
                                )

                            ],
                            height=835,
                            scroll=ft.ScrollMode.ALWAYS,
                            spacing=0,
                            on_scroll=self.record_line
                        )
                    ],
                    width=1050,
                    scroll=ft.ScrollMode.ALWAYS,
                    spacing=0
                )

            ],
            spacing=0,
        )
        running_log("rpy计算完成 更新到page")
        try:
            text_con.update()
        except AssertionError:
            pass
        running_log("更新成功")

    def update_json_txt(self):
        running_log(f"更新 {self.file_name} 的json_info_value")
        self.json_info_value = json.dumps(self.file_json, indent=4, ensure_ascii=False)
        self.line_num["json"] = len(self.json_info_value.split('\n'))

    def update_rpy_txt(self, pb=None):
        running_log(f"更新 {self.file_name} 的rpy_info_value")
        progress_len = len(self.file_json['dialogue']) + len(self.file_json['strings'])
        progress_new = 0
        for event, lines in self.file_json['dialogue'].items():
            progress_new += 1
            if pb is not None and progress_new % 1000 == 0:
                pb.value = progress_new / progress_len
                try:
                    pb.update()
                except AssertionError:
                    return
            for dialogue_hex, line in lines.items():
                line = """# {script}\ntranslate {language} {event}_{dialogue_hex}:\n\n    # {speaker}"{origin}"\n    {speaker}"{translation}"\n\n""".format(
                    script=line['script'],
                    language=self.file_json['language'],
                    event=event,
                    dialogue_hex=dialogue_hex,
                    speaker='' if line['speaker'] == '<>' else '{} '.format(line['speaker']),
                    origin=line['origin'],
                    translation=line['translation']
                )
                self.rpy_info_value += line

        for strings in self.file_json['strings']:
            progress_new += 1
            if pb is not None and progress_new % 1000 == 0:
                pb.value = progress_new / progress_len
                try:
                    pb.update()
                except AssertionError:
                    return
            self.rpy_info_value += 'translate {} strings:\n\n'.format(self.file_json['language'])
            for string in strings:
                string_str = """    # {script}\n    old "{old}"\n    new "{new}"\n\n""".format(
                    script=string['script'],
                    old=string['old'],
                    new=string['new']
                )
                self.rpy_info_value += string_str

        info_value = []
        rpy_info_value_split = self.rpy_info_value.split("\n")
        for line_num, line in enumerate(rpy_info_value_split):
            info_value.append(f"{str(line_num).ljust(6, ' ')} | " + line)
        self.rpy_info_value = "\n".join(info_value)
        self.line_num["rpy"] = len(self.rpy_info_value.split('\n'))

    def switch_to_json_info(self, _):
        running_log(f"显示 {self.file_name} 的json")
        if self.json_info_value == "":
            self.update_json_txt()
        self.showing_type = "json"
        text_con = self.Rm.main_page.controls[3]
        text_control = text_con.content.controls[1].controls[0].controls[0].content
        text_control.value = self.json_info_value
        running_log("json计算完成 更新到page")
        text_control.update()
        running_log("更新成功")

    def switch_to_rpy_info(self, _):
        running_log(f"显示 {self.file_name} 的rpy")
        if self.rpy_info_value == "":
            self.update_rpy_txt()
        self.showing_type = "rpy"
        text_con = self.Rm.main_page.controls[3]
        text_control = text_con.content.controls[1].controls[0].controls[0].content
        text_control.value = self.rpy_info_value
        running_log("rpy计算完成 更新到page")
        text_control.update()
        running_log("更新成功")

    def jump_to(self, e):
        line_txt = e.control.value
        try:
            int(line_txt)
        except ValueError:
            e.control.value = ""
            e.control.update()
            return
        text_Column = self.Rm.main_page.controls[3].content.controls[1].controls[0]
        text_Column.scroll_to(offset=min(float(line_txt), self.line_num[self.showing_type] - 43) * line_height, duration=0)

    def record_line(self, e: ft.OnScrollEvent):
        line_textfield = self.Rm.main_page.controls[3].content.controls[0].controls[0]
        line_textfield.value = str(int(e.pixels / line_height))
        line_textfield.update()

    def text_search(self, _):
        search_textfield = self.Rm.main_page.controls[3].content.controls[0].controls[1]
        search_text = search_textfield.value
        if search_text == "" or search_text is None:
            return
        info = self.rpy_info_value if self.showing_type == "rpy" else self.json_info_value
        search_line = -1
        for line_num, line in enumerate(info.split("\n")):
            if line.find(search_text) != -1:
                search_line = line_num
                break
        if search_line == -1:
            return
        else:
            text_Column = self.Rm.main_page.controls[3].content.controls[1].controls[0]
            text_Column.scroll_to(offset=min(search_line, self.line_num[self.showing_type] - 43) * line_height, duration=0)
            line_textfield = self.Rm.main_page.controls[3].content.controls[0].controls[0]
            line_textfield.value = str(search_line)
            line_textfield.update()


if __name__ == '__main__':
    RPY_File(r"E:\恋爱课程LessonsInLove0.29\0.38翻译文件（还没有整合）\chap3.rpy", None)
