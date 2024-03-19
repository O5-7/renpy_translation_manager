from rpy_file import RPY_File
import flet as ft
import os
import datetime
import json
from rpy_translate_task import rpy_translation_task, date_format
import hashlib
from running_log import running_log


class rpy_version:
    def __init__(self, folder_path: str, version: str, RPY_manager):
        super().__init__()
        self.Rm = RPY_manager

        self.folder_path = folder_path

        self.version = version if version else ''
        self.rpy_dict = {}  # 文件名:文件实例
        self.config = {}
        self.tasks_dict = {}

        self.success: bool = True

        if self.is_init_file():
            self.config = json.load(open(os.path.join(self.folder_path, 'config.json'), mode="r", encoding='utf-8'))
            self.read_rpy_by_json()
        else:
            self.init_running_file()

        task_scan_result = self.scan_tasks()
        if task_scan_result.startswith('no_such'):
            # print(task_scan_result)
            # TODO: tasks扫描错误
            pass

        self.control = self.build_control()

    def update_control(self):
        self.control = self.build_control()

    def switch_files_and_tasks_column(self, _):
        running_log(f"打开version {self.version}")
        self.Rm.selected_version = self.version
        self.Rm.selected_task = ""
        self.Rm.page.controls[0].controls[1].content.content.value = f"RTM >>> {self.version}"
        self.Rm.page.controls[0].controls[1].content.content.update()

        files_column = self.Rm.main_page.controls[2].controls[0].content.content.controls[1]
        files_column: ft.Column
        files_column.controls = [rpy_obj.control for rpy_obj in self.rpy_dict.values()]
        for c in files_column.controls:
            c.visible = True
        files_column.update()

        task_column = self.Rm.main_page.controls[2].controls[1].content.content.controls[1]
        task_column: ft.Column
        self.tasks_dict = {k: self.tasks_dict[k] for k in sorted(self.tasks_dict, reverse=True, key=lambda t: datetime.datetime.strptime(self.tasks_dict[t].host_date, date_format).timestamp())}
        task_column.controls = [task_obj.control for task_obj in self.tasks_dict.values()]
        for c in task_column.controls:
            c.visible = True
        task_column.update()

        self.Rm.main_page.controls[3] = ft.Container(
            ft.Container(width=1060, height=890, bgcolor="#eeeeee"),
            border_radius=5,
            border=ft.border.all(5, "#ff7f00")
        )
        self.Rm.main_page.update()

        for v_control in self.Rm.main_page.controls[1].content.controls[1].controls:
            if v_control.content.content.controls[0].value == self.version:
                v_control.content.border = ft.border.all(5, color="#00ff00")
            else:
                v_control.content.border = ft.border.all(5, color="#83ebac")
            v_control.content.update()

    def build_control(self):
        rpy_v_control = ft.GestureDetector(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f'{self.version}', size=16 if len(self.version) <= 5 else 12, weight=ft.FontWeight.BOLD, color="#2a573b"),
                        ft.Text(f"文件:{len(self.rpy_dict)}", color="#2a573b", size=15),
                        ft.Text(f"任务:{len(self.tasks_dict)}", color="#2a573b", size=15),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                bgcolor="#b7ebc1",
                border=ft.border.all(5, color="#83ebac") if self.success else ft.border.all(5, color="#FF0000"),
                border_radius=5,
                width=100,
                height=100,
            ),
            on_double_tap=self.switch_files_and_tasks_column
        )

        return rpy_v_control

    def init_running_file(self):
        running_log(f"初始化文件 {self.version} {self.folder_path}")
        self.config.update({'version': self.version})
        file_name_list = [file_name[:-4] for file_name in os.listdir(self.folder_path) if file_name.endswith('.rpy')]
        self.config.update({"file_name_list": file_name_list})
        self.read_rpy_by_rpy()
        if not all([rpy_obj.success for rpy_obj in self.rpy_dict.values()]):
            running_log(f"{self.version}: {self.folder_path} 存在格式错误文件 拒绝初始化")
            self.success = False
            return

        event_list = {}
        for file_name in self.config['file_name_list']:
            event_list.update({file_name: list(self.rpy_dict[file_name].file_json['dialogue'].keys())})
        self.config.update({'event_list': event_list})

        for rpy_obj in self.rpy_dict.values():
            rpy_obj: RPY_File
            rpy_obj.write_json(self.folder_path)

        with open(os.path.join(self.folder_path, 'config.json'), mode='w', encoding='utf-8') as F:
            F.write(json.dumps(self.config, indent=2, ensure_ascii=False))

        if not os.path.isdir(os.path.join(self.folder_path, 'tasks')):
            os.mkdir(os.path.join(self.folder_path, 'tasks'))

    def finish_acc(self):
        total = 0
        empty = 0
        for filename in self.config['file_name_list']:
            for event in self.rpy_dict[filename].file_json["dialogue"].values():
                for line in event.values():
                    total += 1
                    if not line["translation"]:
                        empty += 1
        return empty, total, empty / total

    def is_init_file(self):
        return os.path.isfile(os.path.join(self.folder_path, 'config.json'))

    def read_rpy_by_rpy(self, pb=None):
        running_log(f"读取rpys {self.version}")
        self.rpy_dict = {}
        for num, file_name in enumerate(self.config['file_name_list']):
            if pb is not None:
                pb.value = (num + 1) / len(self.config['file_name_list'])
                pb.update()
            rpy = RPY_File(os.path.join(self.folder_path, file_name + '.rpy'), self.Rm)
            self.rpy_dict.update({file_name: rpy})

    def read_rpy_by_json(self, pb=None):
        running_log(f"读取jsons {self.version}")
        self.rpy_dict = {}
        for num, file_name in enumerate(self.config['file_name_list']):
            if pb is not None:
                pb.value = (num + 1) / len(self.config['file_name_list'])
                pb.update()
            rpy = RPY_File(os.path.join(self.folder_path, file_name + '.json'), self.Rm)
            self.rpy_dict.update({file_name: rpy})

    def rpy_2_json(self):
        running_log(f"rpy转移到json {self.version}")

        r2j_dialog = ft.AlertDialog(
            title=ft.Text("rpy转移到json 请勿关闭软件!", size=20, color="#FF0000", font_family="黑体"),
            modal=True,
            actions=[
                ft.Column(
                    [
                        ft.Text("读取中...", size=20),
                        ft.ProgressBar(width=380)
                    ],
                    width=400
                )
            ]
        )

        self.Rm.page.dialog = r2j_dialog
        r2j_dialog.open = True
        self.Rm.page.update()

        self.read_rpy_by_rpy(r2j_dialog.actions[0].controls[1])
        for rpy_num, rpy_obj in enumerate(self.rpy_dict.values()):
            r2j_dialog.actions[0].controls[0].value = rpy_obj.file_name.ljust(20) + f"{(rpy_num + 1)}/{len(self.rpy_dict)}"
            r2j_dialog.actions[0].controls[1].value = (rpy_num + 1) / len(self.rpy_dict)
            r2j_dialog.update()
            if self.success:
                rpy_obj.write_json(self.folder_path)

        self.switch_files_and_tasks_column(None)

        r2j_dialog.open = False
        self.Rm.page.update()

        running_log(f"转移成功 {self.version}")

    def json_2_rpy(self):
        running_log(f"json转移到rpy {self.version}")
        if not self.success:
            running_log("存在解析失败的rpy,操作不允许")
            return
        j2r_dialog = ft.AlertDialog(
            title=ft.Text("json转移到rpy 请勿关闭软件!", size=20, color="#FF0000", font_family="黑体"),
            modal=True,
            actions=[
                ft.Column(
                    [
                        ft.Text("读取中...", size=20),
                        ft.ProgressBar(width=380)
                    ],
                    width=400
                )
            ]
        )
        self.Rm.page.dialog = j2r_dialog
        j2r_dialog.open = True
        self.Rm.page.update()

        self.read_rpy_by_json(j2r_dialog.actions[0].controls[1])
        for rpy_num, rpy_obj in enumerate(self.rpy_dict.values()):
            j2r_dialog.actions[0].controls[0].value = rpy_obj.file_name.ljust(20) + f"{(rpy_num + 1)}/{len(self.rpy_dict)}"
            j2r_dialog.actions[0].controls[1].value = (rpy_num + 1) / len(self.rpy_dict)
            j2r_dialog.update()
            rpy_obj.write_rpy(self.folder_path)

        j2r_dialog.open = False
        self.Rm.page.update()

        running_log(f"转移成功 {self.Rm.selected_version}>>>{self.version}")

    def scan_tasks(self) -> str:
        running_log(f"尝试扫描 {self.Rm.selected_version} 的tasks")
        self.tasks_dict = {}

        tasks_folder_path = os.path.join(self.folder_path, 'tasks')
        if not os.path.isdir(tasks_folder_path):
            running_log(f"任务文件夹 {tasks_folder_path} 不存在")
            return 'no_such_tasks'
        task_file_names = os.listdir(tasks_folder_path)
        running_log(f"扫描tasks {task_file_names}")
        for task_file_name in task_file_names:
            task_name, task_hex = task_file_name[:-5].split('@')
            task_obj = rpy_translation_task(os.path.join(tasks_folder_path, task_file_name), self.Rm)

            # 检查是否匹配当前版本
            task_content = task_obj.task_content
            for file_name, events in task_content.items():
                if file_name not in self.rpy_dict.keys():
                    running_log(f"任务中提及的文件 {file_name} 不存在")
                    return f'no_such_file: {file_name}'
                for event_name, hexs in events.items():
                    if event_name == 'strings':
                        all_strings_hex = []
                        for tr_strings in self.rpy_dict[file_name].file_json['strings']:
                            for strings_line in tr_strings:
                                all_strings_hex.append(hashlib.md5(strings_line['old'].encode(encoding='UTF-8')).hexdigest()[:8])

                        for strings_hex in hexs:
                            if strings_hex != "ALL" and strings_hex not in all_strings_hex:
                                running_log(f"任务中提及的string_hex {strings_hex} 不存在")
                                return f'no_such_string: {strings_hex}'
                        continue

                    if event_name not in self.rpy_dict[file_name].file_json["dialogue"].keys():
                        running_log(f"任务中提及的事件 {event_name} 不存在")
                        return f'no_such_event :{event_name}'
                    for line_hex in hexs:
                        if line_hex == "ALL":
                            break
                        elif line_hex not in self.rpy_dict[file_name].file_json["dialogue"][event_name].keys():
                            running_log(f"任务中提及的line_hex {line_hex} 不存在")
                            return f'no_such_line: {line_hex}'

            self.tasks_dict.update({task_hex: task_obj})
        return 'success'
