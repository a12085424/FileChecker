import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class FileStructureChecker:
    """
    文件结构检查工具 - 带GUI规则设定和列表匹配功能
    """
    def __init__(self):
        self.root_folder = Path(".").resolve()
        self.custom_lists = {}  # 用户自定义列表
        self.folder_rules = {}  # 文件夹规则 {internal_level (0-based): rule_dict}
        self.file_rules = {}    # 文件规则 {internal_level (0-based): rule_dict}
        self.results = []       # 检查结果
        self.setup_gui()

    def setup_gui(self):
        """设置图形界面"""
        self.root = tk.Tk()
        self.root.title("文件结构检查工具 - 规则设定版")
        self.root.geometry("1100x800")
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # 主菜单
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # 规则设定页面（合并自定义列表和规则设定）
        self.setup_rules_tab(notebook)
        # 检查执行页面
        self.setup_check_tab(notebook)
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def setup_rules_tab(self, notebook):
        """设置规则设定页面（合并自定义列表和规则设定）"""
        rules_frame = ttk.Frame(notebook, padding="10")
        notebook.add(rules_frame, text="规则设定")
        # 分成左右两部分
        # 左侧：自定义列表
        left_frame = ttk.Frame(rules_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        # 右侧：规则设定
        right_frame = ttk.Frame(rules_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        # 左侧标题
        ttk.Label(left_frame, text="自定义列表", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        # 列表管理
        list_mgmt_frame = ttk.LabelFrame(left_frame, text="列表管理", padding="10")
        list_mgmt_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_mgmt_frame.columnconfigure(1, weight=1)
        list_mgmt_frame.rowconfigure(1, weight=1)
        # 添加列表
        add_list_frame = ttk.Frame(list_mgmt_frame)
        add_list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(add_list_frame, text="列表名称:").pack(side=tk.LEFT)
        self.list_name_var = tk.StringVar()
        list_name_entry = ttk.Entry(add_list_frame, textvariable=self.list_name_var, width=15)
        list_name_entry.pack(side=tk.LEFT, padx=(10, 10))
        add_list_btn = ttk.Button(add_list_frame, text="添加列表", command=self.add_custom_list)
        add_list_btn.pack(side=tk.LEFT)
        # 列表列表
        lists_display_frame = ttk.Frame(list_mgmt_frame)
        lists_display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        lists_display_frame.columnconfigure(0, weight=1)
        lists_display_frame.rowconfigure(0, weight=1)
        ttk.Label(lists_display_frame, text="已创建的列表:").pack(anchor=tk.W)
        self.lists_listbox = tk.Listbox(lists_display_frame, height=8)
        self.lists_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        # 列表项管理
        items_mgmt_frame = ttk.Frame(list_mgmt_frame)
        items_mgmt_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        items_mgmt_frame.columnconfigure(0, weight=1)
        items_mgmt_frame.rowconfigure(2, weight=1)
        ttk.Label(items_mgmt_frame, text="列表项管理:").pack(anchor=tk.W)
        # 添加列表项
        add_item_frame = ttk.Frame(items_mgmt_frame)
        add_item_frame.pack(fill=tk.X, pady=(5, 10))
        ttk.Label(add_item_frame, text="添加项:").pack(side=tk.LEFT)
        self.list_item_var = tk.StringVar()
        item_entry = ttk.Entry(add_item_frame, textvariable=self.list_item_var, width=15)
        item_entry.pack(side=tk.LEFT, padx=(10, 10))
        add_item_btn = ttk.Button(add_item_frame, text="添加", command=self.add_list_item)
        add_item_btn.pack(side=tk.LEFT)
        # 列表项列表
        ttk.Label(items_mgmt_frame, text="列表项:").pack(anchor=tk.W)
        self.list_items_listbox = tk.Listbox(items_mgmt_frame, height=6)
        self.list_items_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        # 删除按钮
        delete_frame = ttk.Frame(items_mgmt_frame)
        delete_frame.pack(fill=tk.X)
        del_item_btn = ttk.Button(delete_frame, text="删除选中项", command=self.delete_list_item)
        del_item_btn.pack(side=tk.LEFT)
        del_list_btn = ttk.Button(delete_frame, text="删除选中列表", command=self.delete_custom_list)
        del_list_btn.pack(side=tk.LEFT, padx=(10, 0))
        # 右侧标题
        ttk.Label(right_frame, text="规则设定", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        # 路径选择
        path_frame = ttk.LabelFrame(right_frame, text="选择要检查的文件夹", padding="10")
        path_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        ttk.Label(path_frame, text="文件夹路径:").grid(row=0, column=0, sticky=tk.W)
        self.path_var = tk.StringVar(value=str(self.root_folder))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=0, column=1, padx=(10, 10), sticky=(tk.W, tk.E))
        browse_btn = ttk.Button(path_frame, text="浏览...", command=self.browse_folder)
        browse_btn.grid(row=0, column=2)
        # 文件夹规则设定
        folder_rules_frame = ttk.LabelFrame(right_frame, text="文件夹命名规则", padding="10")
        folder_rules_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        folder_rules_frame.columnconfigure(0, weight=1)
        folder_rules_frame.rowconfigure(1, weight=1)
        # 文件夹规则按钮
        folder_btn_frame = ttk.Frame(folder_rules_frame)
        folder_btn_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        add_folder_btn = ttk.Button(folder_btn_frame, text="添加规则", command=self.add_folder_rule)
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        edit_folder_btn = ttk.Button(folder_btn_frame, text="编辑规则", command=self.edit_folder_rule)
        edit_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        del_folder_btn = ttk.Button(folder_btn_frame, text="删除规则", command=self.delete_folder_rule)
        del_folder_btn.pack(side=tk.LEFT)
        # 文件夹规则列表
        self.folder_rules_listbox = tk.Listbox(folder_rules_frame, height=6)
        self.folder_rules_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        folder_rules_scrollbar = ttk.Scrollbar(folder_rules_frame, orient="vertical", command=self.folder_rules_listbox.yview)
        folder_rules_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.folder_rules_listbox.configure(yscrollcommand=folder_rules_scrollbar.set)
        # 文件规则设定
        file_rules_frame = ttk.LabelFrame(right_frame, text="文件命名规则", padding="10")
        file_rules_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_rules_frame.columnconfigure(0, weight=1)
        file_rules_frame.rowconfigure(1, weight=1)
        # 文件规则按钮
        file_btn_frame = ttk.Frame(file_rules_frame)
        file_btn_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        add_file_btn = ttk.Button(file_btn_frame, text="添加规则", command=self.add_file_rule)
        add_file_btn.pack(side=tk.LEFT, padx=(0, 5))
        edit_file_btn = ttk.Button(file_btn_frame, text="编辑规则", command=self.edit_file_rule)
        edit_file_btn.pack(side=tk.LEFT, padx=(0, 5))
        del_file_btn = ttk.Button(file_btn_frame, text="删除规则", command=self.delete_file_rule)
        del_file_btn.pack(side=tk.LEFT)
        # 文件规则列表
        self.file_rules_listbox = tk.Listbox(file_rules_frame, height=6)
        self.file_rules_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_rules_scrollbar = ttk.Scrollbar(file_rules_frame, orient="vertical", command=self.file_rules_listbox.yview)
        file_rules_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.file_rules_listbox.configure(yscrollcommand=file_rules_scrollbar.set)
        # 常用模式说明
        help_frame = ttk.LabelFrame(right_frame, text="常用模式说明", padding="5")
        help_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        help_frame.columnconfigure(0, weight=1)
        help_text = """
        常用模式：
        \\d{4} - 4位数字    \\d+ - 任意位数数字    (选项1|选项2) - 多选一
        [年份4位] - 4位年份    [数字] - 数字    [日期8位] - 8位日期
        [任意字符] - 任意字符    [字母] - 字母    [汉字] - 汉字
        [列表名] - 使用自定义列表中的值
        层级说明：
        1 - 根目录下的第一层文件夹/文件
        2 - 第二层文件夹/文件
        """
        help_label = ttk.Label(help_frame, text=help_text)
        help_label.grid(row=0, column=0, sticky=tk.W)
        rules_frame.columnconfigure(0, weight=1)
        rules_frame.columnconfigure(1, weight=2)
        rules_frame.rowconfigure(0, weight=1)

    def setup_check_tab(self, notebook):
        """设置检查执行页面"""
        check_frame = ttk.Frame(notebook, padding="10")
        notebook.add(check_frame, text="执行检查")
        # 操作按钮
        button_frame = ttk.Frame(check_frame)
        button_frame.grid(row=0, column=0, pady=(0, 20))
        self.check_btn = ttk.Button(button_frame, text="开始检查", command=self.run_check_gui)
        self.check_btn.grid(row=0, column=0, padx=(0, 10))
        self.save_btn = ttk.Button(button_frame, text="保存结果", command=self.save_results, state=tk.DISABLED)
        self.save_btn.grid(row=0, column=1, padx=(0, 10))
        # 结果显示
        result_frame = ttk.LabelFrame(check_frame, text="检查结果", padding="10")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=25, width=100)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        check_frame.columnconfigure(0, weight=1)
        check_frame.rowconfigure(1, weight=1)

    # 自定义列表管理方法
    def add_custom_list(self):
        """添加自定义列表"""
        list_name = self.list_name_var.get().strip()
        if not list_name:
            messagebox.showerror("错误", "请输入列表名称！")
            return
        if list_name in self.custom_lists:
            messagebox.showerror("错误", f"列表 '{list_name}' 已存在！")
            return
        self.custom_lists[list_name] = []
        self.list_name_var.set("")
        self.update_lists_display()

    def delete_custom_list(self):
        """删除自定义列表"""
        selection = self.lists_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的列表！")
            return
        list_name = self.lists_listbox.get(selection[0])
        if messagebox.askyesno("确认", f"确定要删除列表 '{list_name}' 吗？"):
            if list_name in self.custom_lists:
                del self.custom_lists[list_name]
                self.update_lists_display()
                self.list_items_listbox.delete(0, tk.END)

    def add_list_item(self):
        """添加列表项"""
        selection = self.lists_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个列表！")
            return
        list_name = self.lists_listbox.get(selection[0])
        item_value = self.list_item_var.get().strip()
        if not item_value:
            messagebox.showerror("错误", "请输入列表项内容！")
            return
        if item_value in self.custom_lists[list_name]:
            messagebox.showerror("错误", f"列表项 '{item_value}' 已存在！")
            return
        self.custom_lists[list_name].append(item_value)
        self.list_item_var.set("")
        self.update_list_items_display(list_name)

    def delete_list_item(self):
        """删除列表项 - 实时更新显示"""
        item_selection = self.list_items_listbox.curselection()
        if item_selection:
            # 获取选中的列表项
            item_value = self.list_items_listbox.get(item_selection[0])
            # 获取当前选中的列表
            list_selection = self.lists_listbox.curselection()
            deleted = False
            if list_selection:
                # 如果有选中的列表，直接从该列表删除
                list_name = self.lists_listbox.get(list_selection[0])
                if list_name in self.custom_lists and item_value in self.custom_lists[list_name]:
                    if messagebox.askyesno("确认", f"确定要删除列表项 '{item_value}' 吗？"):
                        self.custom_lists[list_name].remove(item_value)
                        # 实时更新显示
                        self.update_list_items_display(list_name)
                        deleted = True
            else:
                # 如果没有选中列表，但在列表项列表中选中了项，尝试从所有列表中查找
                for list_name in self.custom_lists:
                    if item_value in self.custom_lists[list_name]:
                        if messagebox.askyesno("确认", f"确定要删除列表项 '{item_value}' 吗？"):
                            self.custom_lists[list_name].remove(item_value)
                            # 实时更新显示
                            self.update_list_items_display(list_name)
                            deleted = True
                        break
            # 如果删除成功，清除选中状态
            if deleted:
                self.list_items_listbox.selection_clear(0, tk.END)
        else:
            messagebox.showwarning("警告", "请先选择要删除的列表项！")

    def update_lists_display(self):
        """更新列表显示"""
        self.lists_listbox.delete(0, tk.END)
        for list_name in sorted(self.custom_lists.keys()):
            self.lists_listbox.insert(tk.END, list_name)

    def update_list_items_display(self, list_name):
        """更新列表项显示 - 实时更新"""
        self.list_items_listbox.delete(0, tk.END)
        if list_name in self.custom_lists:
            for item in self.custom_lists[list_name]:
                self.list_items_listbox.insert(tk.END, item)
        # 强制刷新界面
        self.list_items_listbox.update_idletasks()

    def on_list_selected(self, event):
        """列表选择事件"""
        selection = self.lists_listbox.curselection()
        if selection:
            list_name = self.lists_listbox.get(selection[0])
            self.update_list_items_display(list_name)

    # 规则编辑功能
    def edit_folder_rule(self):
        """编辑文件夹规则"""
        selection = self.folder_rules_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的规则！")
            return
        # 从显示列表中获取层级
        selected_text = self.folder_rules_listbox.get(selection[0])
        try:
            user_level = int(selected_text.split(':')[0].split()[1])
            internal_level = user_level - 1  # 转换为内部层级
            # 获取现有规则
            if internal_level in self.folder_rules:
                existing_rule = self.folder_rules[internal_level]
                # 打开编辑对话框
                dialog = EditRuleDialog(
                    self.root, 
                    "编辑文件夹规则", 
                    "folder", 
                    list(self.custom_lists.keys()),
                    internal_level + 1,  # 转换回用户层级
                    existing_rule
                )
                self.root.wait_window(dialog.dialog)
                if dialog.result:
                    # 更新规则
                    new_level = dialog.result['level']
                    new_internal_level = new_level - 1  # 转换为内部层级
                    # 如果层级改变了，需要删除旧规则
                    if new_internal_level != internal_level:
                        del self.folder_rules[internal_level]
                    self.folder_rules[new_internal_level] = {
                        'pattern': dialog.result['pattern'],
                        'description': dialog.result['description'],
                        'list_matching': dialog.result.get('list_matching', {})
                    }
                    # 更新显示
                    self.update_folder_rules_list()
            else:
                messagebox.showerror("错误", "找不到对应的规则！")
        except Exception as e:
            messagebox.showerror("错误", f"解析规则信息失败：{str(e)}")

    def edit_file_rule(self):
        """编辑文件规则"""
        selection = self.file_rules_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的规则！")
            return
        # 从显示列表中获取层级
        selected_text = self.file_rules_listbox.get(selection[0])
        try:
            user_level = int(selected_text.split(':')[0].split()[1])
            internal_level = user_level - 1  # 转换为内部层级
            # 获取现有规则
            if internal_level in self.file_rules:
                existing_rule = self.file_rules[internal_level]
                # 打开编辑对话框
                dialog = EditRuleDialog(
                    self.root, 
                    "编辑文件规则", 
                    "file", 
                    list(self.custom_lists.keys()),
                    internal_level + 1,  # 转换回用户层级
                    existing_rule
                )
                self.root.wait_window(dialog.dialog)
                if dialog.result:
                    # 更新规则
                    new_level = dialog.result['level']
                    new_internal_level = new_level - 1  # 转换为内部层级
                    # 如果层级改变了，需要删除旧规则
                    if new_internal_level != internal_level:
                        del self.file_rules[internal_level]
                    self.file_rules[new_internal_level] = {
                        'pattern': dialog.result['pattern'],
                        'extensions': dialog.result['extensions'],
                        'description': dialog.result['description'],
                        'list_matching': dialog.result.get('list_matching', {})
                    }
                    # 更新显示
                    self.update_file_rules_list()
            else:
                messagebox.showerror("错误", "找不到对应的规则！")
        except Exception as e:
            messagebox.showerror("错误", f"解析规则信息失败：{str(e)}")

    # 其他原有方法保持不变...
    def browse_folder(self):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_var.set(folder_path)
            self.root_folder = Path(folder_path)

    def add_folder_rule(self):
        """添加文件夹规则"""
        dialog = RuleDialog(self.root, "添加文件夹规则", "folder", list(self.custom_lists.keys()))
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            level = dialog.result['level']
            pattern = dialog.result['pattern']
            description = dialog.result['description']
            list_matching = dialog.result.get('list_matching', {})
            # 转换层级：用户输入的1对应内部的0
            internal_level = level - 1
            self.folder_rules[internal_level] = {
                'pattern': pattern,
                'description': description,
                'list_matching': list_matching
            }
            # 更新列表显示
            self.update_folder_rules_list()

    def add_file_rule(self):
        """添加文件规则"""
        dialog = RuleDialog(self.root, "添加文件规则", "file", list(self.custom_lists.keys()))
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            level = dialog.result['level']
            pattern = dialog.result['pattern']
            extensions = dialog.result['extensions']
            description = dialog.result['description']
            list_matching = dialog.result.get('list_matching', {})
            # 转换层级：用户输入的1对应内部的0
            internal_level = level - 1
            self.file_rules[internal_level] = {
                'pattern': pattern,
                'extensions': extensions,
                'description': description,
                'list_matching': list_matching
            }
            # 更新列表显示
            self.update_file_rules_list()

    def delete_folder_rule(self):
        """删除文件夹规则"""
        selection = self.folder_rules_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的规则！")
            return
        # 从显示列表中获取层级
        selected_text = self.folder_rules_listbox.get(selection[0])
        # 解析显示文本中的层级（显示的是用户层级，需要转换为内部层级）
        try:
            user_level = int(selected_text.split(':')[0].split()[1])
            internal_level = user_level - 1  # 转换为内部层级
            # 删除规则
            if internal_level in self.folder_rules:
                del self.folder_rules[internal_level]
                self.update_folder_rules_list()
            else:
                messagebox.showerror("错误", "找不到对应的规则！")
        except Exception as e:
            messagebox.showerror("错误", f"解析规则层级失败：{str(e)}")

    def delete_file_rule(self):
        """删除文件规则"""
        selection = self.file_rules_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的规则！")
            return
        # 从显示列表中获取层级
        selected_text = self.file_rules_listbox.get(selection[0])
        # 解析显示文本中的层级（显示的是用户层级，需要转换为内部层级）
        try:
            user_level = int(selected_text.split(':')[0].split()[1])
            internal_level = user_level - 1  # 转换为内部层级
            # 删除规则
            if internal_level in self.file_rules:
                del self.file_rules[internal_level]
                self.update_file_rules_list()
            else:
                messagebox.showerror("错误", "找不到对应的规则！")
        except Exception as e:
            messagebox.showerror("错误", f"解析规则层级失败：{str(e)}")

    def update_folder_rules_list(self):
        """更新文件夹规则列表显示"""
        self.folder_rules_listbox.delete(0, tk.END)
        for level in sorted(self.folder_rules.keys()):
            rule = self.folder_rules[level]
            matching_info = ""
            if rule.get('list_matching'):
                matching_lists = [f"{k}={v}" for k, v in rule['list_matching'].items()]
                matching_info = f" [匹配: {', '.join(matching_lists)}]"
            # 显示时转换回用户理解的层级
            user_level = level + 1
            self.folder_rules_listbox.insert(tk.END, f"第 {user_level} 层: {rule['pattern']} - {rule['description']}{matching_info}")

    def update_file_rules_list(self):
        """更新文件规则列表显示"""
        self.file_rules_listbox.delete(0, tk.END)
        for level in sorted(self.file_rules.keys()):
            rule = self.file_rules[level]
            ext_str = ', '.join(rule['extensions']) if rule['extensions'] else '无限制'
            matching_info = ""
            if rule.get('list_matching'):
                matching_lists = [f"{k}={v}" for k, v in rule['list_matching'].items()]
                matching_info = f" [匹配: {', '.join(matching_lists)}]"
            # 显示时转换回用户理解的层级
            user_level = level + 1
            self.file_rules_listbox.insert(tk.END, f"第 {user_level} 层: {rule['pattern']} [{ext_str}] - {rule['description']}{matching_info}")

    def extract_list_values(self, name: str, pattern: str) -> Dict[str, str]:
        """从名称中提取列表值"""
        list_values = {}
        # 找出模式中包含的所有列表
        list_matches = re.findall(r'\[([^\]]+)\]', pattern)
        for list_name in list_matches:
            if list_name in self.custom_lists:
                list_items = self.custom_lists[list_name]
                # 按长度降序排列，优先匹配长的项
                sorted_items = sorted(list_items, key=len, reverse=True)
                # 在名称中查找列表项
                for item in sorted_items:
                    if item in name:
                        list_values[list_name] = item
                        break
        return list_values

    def check_name_pattern(self, name: str, pattern: str) -> Tuple[bool, Dict[str, str]]:
        """检查名称是否符合模式，返回匹配结果和提取的列表值"""
        try:
            # 先处理预定义模式和自定义列表
            processed_pattern = pattern
            # 预定义的常用模式
            predefined_patterns = {
                '[年份4位]': r'(\d{4})',
                '[数字]': r'(\d+)',
                '[日期8位]': r'(\d{8})',
                '[任意字符]': r'(.*)',
                '[字母]': r'([a-zA-Z]+)',
                '[汉字]': r'([\u4e00-\u9fff]+)'
            }
            # 替换预定义模式
            for placeholder, regex_pattern in predefined_patterns.items():
                processed_pattern = processed_pattern.replace(placeholder, regex_pattern)
            # 处理自定义列表
            list_values = {}
            list_placeholders = []
            # 找出所有列表占位符
            list_matches = re.findall(r'\[([^\]]+)\]', processed_pattern)
            for list_name in list_matches:
                if list_name in self.custom_lists:
                    list_items = self.custom_lists[list_name]
                    # 转义列表项并用|连接（按长度降序排列）
                    sorted_items = sorted(list_items, key=len, reverse=True)
                    escaped_items = [re.escape(item) for item in sorted_items]
                    list_pattern = f'({"|".join(escaped_items)})'
                    processed_pattern = processed_pattern.replace(f'[{list_name}]', list_pattern, 1)
                    list_placeholders.append(list_name)
            # 确保整个字符串匹配
            final_pattern = f"^{processed_pattern}$"
            # 进行匹配
            match_result = re.match(final_pattern, name)
            if match_result:
                # 提取列表值
                list_values = self.extract_list_values(name, pattern)
                return True, list_values
            else:
                return False, {}
        except Exception as e:
            print(f"模式匹配错误: {e}")
            return False, {}

    def check_extension(self, file_path: Path, allowed_extensions: List[str]) -> bool:
        """检查文件扩展名"""
        if not allowed_extensions:
            return True
        file_ext = file_path.suffix.lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]

    def check_recursive(self, current_path: Path, level: int = 0, parent_list_values: Dict[str, str] = None):
        """递归检查文件夹结构，包含列表匹配检查"""
        if parent_list_values is None:
            parent_list_values = {}
        try:
            items = list(current_path.iterdir())
            folders = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            # --- 核心修复1: 正确初始化 current_list_values ---
            # 始终从 parent_list_values 复制，确保包含所有上级信息
            current_list_values = parent_list_values.copy()

            # --- 核心修复2: 文件夹规则层级逻辑 ---
            # 只有当 level > 0 时，才检查当前文件夹的命名规则
            # level = 0 时，current_path 是用户选择的根目录，不检查其命名规则
            # level = 1 时，current_path 是根目录下的第一层文件夹，对应用户层级1的规则
            if level > 0:
                # 使用 level - 1 作为键来查找文件夹规则
                # 这样 level=1 时查找 self.folder_rules[0] (用户层级1)
                #    level=2 时查找 self.folder_rules[1] (用户层级2)
                folder_level_to_check = level - 1 
                if folder_level_to_check in self.folder_rules:
                    rule = self.folder_rules[folder_level_to_check]
                    pattern = rule['pattern']
                    if pattern:
                        is_match, extracted_values = self.check_name_pattern(current_path.name, pattern)
                        if not is_match:
                            self.results.append({
                                'type': '文件夹命名错误',
                                'path': str(current_path),
                                'level': folder_level_to_check + 1,  # 显示用户层级
                                'message': f"文件夹 '{current_path.name}' 命名不符合要求: {rule['description']}",
                                'expected': pattern,
                                'actual_name': current_path.name
                            })
                        else:
                            # --- 核心修复3: 更新 current_list_values 供子文件/文件夹使用 ---
                            # 文件夹命名匹配成功，将其提取的列表值合并到 current_list_values
                            # 这样，current_list_values 现在包含了：
                            # 1. 祖父级及更上级传递下来的列表值 (parent_list_values.copy())
                            # 2. 当前文件夹 newly 提取到的列表值 (extracted_values)
                            current_list_values.update(extracted_values)
                            
                            # 检查列表匹配规则 (文件夹与上级文件夹的列表值比较)
                            list_matching = rule.get('list_matching', {})
                            for list_name, should_match_parent in list_matching.items():
                                # 检查条件：
                                # 1. 规则要求匹配 (should_match_parent is True)
                                # 2. 父级(祖父级)有此列表值 (list_name in parent_list_values)
                                # 3. 当前文件夹也提取到了此列表值 (list_name in extracted_values)
                                if should_match_parent and list_name in parent_list_values and list_name in extracted_values:
                                    # 比较父级列表值和当前文件夹提取的列表值是否相同
                                    if parent_list_values[list_name] != extracted_values[list_name]:
                                        self.results.append({
                                            'type': '列表匹配错误',
                                            'path': str(current_path),
                                            'level': folder_level_to_check + 1,  # 显示用户层级
                                            'message': f"文件夹 '{current_path.name}' 中的列表 '{list_name}' 值 '{extracted_values[list_name]}' 与上级文件夹值 '{parent_list_values[list_name]}' 不匹配",
                                            'expected': pattern,
                                            'actual_name': current_path.name
                                        })

            # 检查当前层级的文件 (文件规则层级逻辑保持不变)
            # level = 0 时检查根目录下的文件 (用户层级1)
            # level = 1 时检查根目录下第一层文件夹内的文件 (用户层级2)
            file_level = level
            if file_level in self.file_rules:
                rule = self.file_rules[file_level]
                pattern = rule['pattern']
                extensions = rule['extensions']
                for file_path in files:
                    # 检查文件命名
                    if pattern:
                        is_match, extracted_values = self.check_name_pattern(file_path.stem, pattern)
                        if not is_match:
                            self.results.append({
                                'type': '文件命名错误',
                                'path': str(file_path),
                                'level': file_level + 1,  # 显示用户层级
                                'message': f"文件 '{file_path.name}' 命名不符合要求: {rule['description']}",
                                'expected': pattern,
                                'actual_name': file_path.stem
                            })
                        else:
                            # --- 核心修复4: 文件列表匹配检查使用更新后的 current_list_values ---
                            # 关键点: 文件列表匹配检查使用 current_list_values 而不是 parent_list_values
                            # current_list_values 包含了：
                            # 1. 祖父级的列表值 (从递归调用传入)
                            # 2. 如果直接父文件夹命名匹配成功，还包含了直接父文件夹的列表值
                            # 这使得文件可以与其直接父文件夹(如果父文件夹命名匹配)或祖父级文件夹进行列表值比较
                            
                            list_matching = rule.get('list_matching', {})
                            for list_name, should_match_parent in list_matching.items():
                                # 检查条件：
                                # 1. 规则要求匹配 (should_match_parent is True)
                                # 2. 父级(直接父文件夹)有此列表值 (list_name in current_list_values)
                                #    这里的 current_list_values 是经过文件夹检查后可能更新的
                                # 3. 当前文件也提取到了此列表值 (list_name in extracted_values)
                                if should_match_parent and list_name in current_list_values and list_name in extracted_values:
                                    # 比较父级列表值和当前文件提取的列表值是否相同
                                    # 修复点: 错误信息中也使用 current_list_values 的值，保持一致性
                                    if current_list_values[list_name] != extracted_values[list_name]:
                                        self.results.append({
                                            'type': '列表匹配错误',
                                            'path': str(file_path),
                                            'level': file_level + 1,  # 显示用户层级
                                            'message': f"文件 '{file_path.name}' 中的列表 '{list_name}' 值 '{extracted_values[list_name]}' 与上级文件夹值 '{current_list_values[list_name]}' 不匹配",
                                            'expected': pattern,
                                            'actual_name': file_path.stem
                                        })
                    # 检查文件扩展名
                    if extensions:
                        if not self.check_extension(file_path, extensions):
                            self.results.append({
                                'type': '文件扩展名错误',
                                'path': str(file_path),
                                'level': file_level + 1,  # 显示用户层级
                                'message': f"文件 '{file_path.name}' 扩展名不符合要求，应为: {', '.join(extensions)}",
                                'expected': extensions
                            })

            # 递归检查子文件夹
            for folder in folders:
                # 传递更新后的 current_list_values
                # 这确保了子文件夹和子文件能接收到当前文件夹(如果命名匹配)和所有上级文件夹的列表值
                self.check_recursive(folder, level + 1, current_list_values)
        except PermissionError:
            self.results.append({
                'type': '权限错误',
                'path': str(current_path),
                'level': level + 1,  # 显示用户层级
                'message': f"无法访问文件夹 '{current_path}'，权限不足"
            })
        except Exception as e:
            self.results.append({
                'type': '检查错误',
                'path': str(current_path),
                'level': level + 1,  # 显示用户层级
                'message': f"检查文件夹 '{current_path}' 时出错: {str(e)}"
            })

    def run_check_gui(self):
        """GUI版本的运行检查"""
        self.check_btn.config(state=tk.DISABLED, text="检查中...")
        self.root.update()
        try:
            self.results = []
            if not self.root_folder.exists():
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, f"❌ 错误：根目录不存在: {self.root_folder}")
                return
            self.check_recursive(self.root_folder)
            # 显示结果
            self.result_text.delete(1.0, tk.END)
            if not self.results:
                self.result_text.insert(1.0, "🎉 恭喜！所有文件结构都符合要求。\n")
                self.result_text.insert(tk.END, "✅ 文件夹结构完全正确，无需修改。")
            else:
                self.result_text.insert(1.0, f"❌ 发现 {len(self.results)} 个问题需要修正：\n")
                for i, result in enumerate(self.results, 1):
                    self.result_text.insert(tk.END, f"{i}. [{result['type']}]\n")
                    self.result_text.insert(tk.END, f"   路径: {result['path']}\n")
                    self.result_text.insert(tk.END, f"   问题: {result['message']}\n")
                    if 'actual_name' in result:
                        self.result_text.insert(tk.END, f"   实际名称: {result['actual_name']}\n")
                    if 'expected' in result:
                        self.result_text.insert(tk.END, f"   期望模式: {result['expected']}\n")
                    self.result_text.insert(tk.END, "\n")
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"❌ 检查过程中出现错误：\n{str(e)}")
        finally:
            self.check_btn.config(state=tk.NORMAL, text="开始检查")

    def save_results(self):
        """保存结果到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                content = self.result_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"结果已保存到：\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：\n{str(e)}")

    def run(self):
        """运行GUI"""
        # 绑定列表选择事件
        self.lists_listbox.bind('<<ListboxSelect>>', self.on_list_selected)
        self.root.mainloop()

class RuleDialog:
    """规则设定对话框"""
    def __init__(self, parent, title: str, rule_type: str, available_lists: List[str]):
        self.result = None
        self.rule_type = rule_type
        self.available_lists = available_lists
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.setup_dialog()

    def setup_dialog(self):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        # 层级设定
        level_frame = ttk.Frame(main_frame)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(level_frame, text="层级:").pack(side=tk.LEFT)
        self.level_var = tk.StringVar(value="1")
        level_entry = ttk.Entry(level_frame, textvariable=self.level_var, width=10)
        level_entry.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(level_frame, text="(1表示根目录下第一层，2表示第二层……)").pack(side=tk.LEFT, padx=(10, 0))
        # 命名模式
        pattern_frame = ttk.Frame(main_frame)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(pattern_frame, text="命名模式:").pack(anchor=tk.W)
        self.pattern_var = tk.StringVar()
        pattern_entry = ttk.Entry(pattern_frame, textvariable=self.pattern_var)
        pattern_entry.pack(fill=tk.X, pady=(5, 0))
        # 列表匹配设置
        list_matching_frame = ttk.LabelFrame(main_frame, text="列表匹配设置", padding="10")
        list_matching_frame.pack(fill=tk.X, pady=(0, 10))
        if self.rule_type == "folder":
            ttk.Label(list_matching_frame, text="选择需要与上级匹配的列表（文件夹规则）:").pack(anchor=tk.W)
        else:
            ttk.Label(list_matching_frame, text="选择需要与上级匹配的列表（文件规则）:").pack(anchor=tk.W)
        self.list_matching_vars = {}
        for list_name in self.available_lists:
            var = tk.BooleanVar(value=True)  # 默认勾选
            self.list_matching_vars[list_name] = var
            checkbox = ttk.Checkbutton(list_matching_frame, text=list_name, variable=var)
            checkbox.pack(anchor=tk.W)
        # 描述
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(desc_frame, text="规则描述:").pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var)
        desc_entry.pack(fill=tk.X, pady=(5, 0))
        # 文件扩展名（仅文件规则）
        if self.rule_type == "file":
            ext_frame = ttk.Frame(main_frame)
            ext_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(ext_frame, text="允许的扩展名:").pack(anchor=tk.W)
            ttk.Label(ext_frame, text="(用逗号分隔，如: .pdf,.doc,.docx)").pack(anchor=tk.W)
            self.ext_var = tk.StringVar()
            ext_entry = ttk.Entry(ext_frame, textvariable=self.ext_var)
            ext_entry.pack(fill=tk.X, pady=(5, 0))
        # 常用模式说明
        help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        help_text = """
        命名模式示例：
        文件夹：思维[年级]  →  思维一年级
        文件夹：\\d{1,2}班  →  1班, 2班
        文件：课程介绍_\\d{8}  →  课程介绍_20231201
        文件：[年级][学科]课件  →  一年级语文课件
        自定义列表使用：[列表名]
        例如：[年级] 将匹配你创建的年级列表中的任意一项
        列表匹配：勾选列表名后，会检查当前文件/文件夹中的列表值是否与上级文件夹相同
        预定义模式：
        [年份4位]  →  \\d{4}
        [数字]  →  \\d+
        [日期8位]  →  \\d{8}
        [任意字符]  →  任意字符
        """
        help_text_widget = tk.Text(help_frame, height=6, wrap=tk.WORD)
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state=tk.DISABLED)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        ok_btn = ttk.Button(button_frame, text="确定", command=self.ok)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)

    def ok(self):
        """确定按钮处理"""
        try:
            level = int(self.level_var.get())
            if level < 1:
                messagebox.showerror("错误", "层级必须大于等于1！")
                return
            pattern = self.pattern_var.get().strip()
            description = self.desc_var.get().strip()
            if not pattern:
                messagebox.showerror("错误", "请填写命名模式！")
                return
            self.result = {
                'level': level,
                'pattern': pattern,
                'description': description
            }
            # 处理列表匹配设置
            list_matching = {}
            for list_name, var in self.list_matching_vars.items():
                if var.get():
                    list_matching[list_name] = True
            self.result['list_matching'] = list_matching
            if self.rule_type == "file":
                extensions = [ext.strip() for ext in self.ext_var.get().split(',') if ext.strip()]
                self.result['extensions'] = extensions
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("错误", "层级必须是数字！")

    def cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()

class EditRuleDialog:
    """编辑规则对话框"""
    def __init__(self, parent, title: str, rule_type: str, available_lists: List[str], level: int, existing_rule: dict):
        self.result = None
        self.rule_type = rule_type
        self.available_lists = available_lists
        self.existing_rule = existing_rule
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.setup_dialog(level)

    def setup_dialog(self, level):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        # 层级设定
        level_frame = ttk.Frame(main_frame)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(level_frame, text="层级:").pack(side=tk.LEFT)
        self.level_var = tk.StringVar(value=str(level))
        level_entry = ttk.Entry(level_frame, textvariable=self.level_var, width=10)
        level_entry.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(level_frame, text="(1表示根目录下第一层，2表示第二层……)").pack(side=tk.LEFT, padx=(10, 0))
        # 命名模式
        pattern_frame = ttk.Frame(main_frame)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(pattern_frame, text="命名模式:").pack(anchor=tk.W)
        self.pattern_var = tk.StringVar(value=self.existing_rule.get('pattern', ''))
        pattern_entry = ttk.Entry(pattern_frame, textvariable=self.pattern_var)
        pattern_entry.pack(fill=tk.X, pady=(5, 0))
        # 列表匹配设置
        list_matching_frame = ttk.LabelFrame(main_frame, text="列表匹配设置", padding="10")
        list_matching_frame.pack(fill=tk.X, pady=(0, 10))
        if self.rule_type == "folder":
            ttk.Label(list_matching_frame, text="选择需要与上级匹配的列表（文件夹规则）:").pack(anchor=tk.W)
        else:
            ttk.Label(list_matching_frame, text="选择需要与上级匹配的列表（文件规则）:").pack(anchor=tk.W)
        self.list_matching_vars = {}
        existing_matching = self.existing_rule.get('list_matching', {})
        for list_name in self.available_lists:
            var = tk.BooleanVar(value=list_name in existing_matching)
            self.list_matching_vars[list_name] = var
            checkbox = ttk.Checkbutton(list_matching_frame, text=list_name, variable=var)
            checkbox.pack(anchor=tk.W)
        # 描述
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(desc_frame, text="规则描述:").pack(anchor=tk.W)
        self.desc_var = tk.StringVar(value=self.existing_rule.get('description', ''))
        desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var)
        desc_entry.pack(fill=tk.X, pady=(5, 0))
        # 文件扩展名（仅文件规则）
        if self.rule_type == "file":
            ext_frame = ttk.Frame(main_frame)
            ext_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(ext_frame, text="允许的扩展名:").pack(anchor=tk.W)
            ttk.Label(ext_frame, text="(用逗号分隔，如: .pdf,.doc,.docx)").pack(anchor=tk.W)
            ext_str = ','.join(self.existing_rule.get('extensions', []))
            self.ext_var = tk.StringVar(value=ext_str)
            ext_entry = ttk.Entry(ext_frame, textvariable=self.ext_var)
            ext_entry.pack(fill=tk.X, pady=(5, 0))
        # 常用模式说明
        help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        help_text = """
        命名模式示例：
        文件夹：思维[年级]  →  思维一年级
        文件夹：\\d{1,2}班  →  1班, 2班
        文件：课程介绍_\\d{8}  →  课程介绍_20231201
        文件：[年级][学科]课件  →  一年级语文课件
        自定义列表使用：[列表名]
        例如：[年级] 将匹配你创建的年级列表中的任意一项
        列表匹配：勾选列表名后，会检查当前文件/文件夹中的列表值是否与上级文件夹相同
        预定义模式：
        [年份4位]  →  \\d{4}
        [数字]  →  \\d+
        [日期8位]  →  \\d{8}
        [任意字符]  →  任意字符
        """
        help_text_widget = tk.Text(help_frame, height=6, wrap=tk.WORD)
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state=tk.DISABLED)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        ok_btn = ttk.Button(button_frame, text="确定", command=self.ok)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)

    def ok(self):
        """确定按钮处理"""
        try:
            level = int(self.level_var.get())
            if level < 1:
                messagebox.showerror("错误", "层级必须大于等于1！")
                return
            pattern = self.pattern_var.get().strip()
            description = self.desc_var.get().strip()
            if not pattern:
                messagebox.showerror("错误", "请填写命名模式！")
                return
            self.result = {
                'level': level,
                'pattern': pattern,
                'description': description
            }
            # 处理列表匹配设置
            list_matching = {}
            for list_name, var in self.list_matching_vars.items():
                if var.get():
                    list_matching[list_name] = True
            self.result['list_matching'] = list_matching
            if self.rule_type == "file":
                extensions = [ext.strip() for ext in self.ext_var.get().split(',') if ext.strip()]
                self.result['extensions'] = extensions
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("错误", "层级必须是数字！")

    def cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()

def main():
    """主函数"""
    print("正在启动文件结构检查工具...")
    app = FileStructureChecker()
    app.run()

if __name__ == "__main__":
    main()