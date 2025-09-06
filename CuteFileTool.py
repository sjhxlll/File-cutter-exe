# 导入我们需要的所有魔法模块
import os
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# --- 后端逻辑部分 (有修改) ---

def split_file_logic(file_path, chunk_size_str, unit, status_callback,
                     output_dir_path=None):  # <--- 增加 output_dir_path 参数
    """文件切割的核心逻辑"""
    try:
        chunk_size = int(chunk_size_str)
        if chunk_size <= 0:
            raise ValueError("大小必须是正数哦")

        if unit == 'KB':
            chunk_size_bytes = chunk_size * 1024
        elif unit == 'MB':
            chunk_size_bytes = chunk_size * 1024 * 1024
        else:
            raise ValueError("未知的单位")

        status_callback(f"准备开始切割 '{os.path.basename(file_path)}'...")

        file_dir, file_name = os.path.split(file_path)

        # --- 修改：判断是否使用了自定义输出目录 ---
        if output_dir_path and os.path.isdir(output_dir_path):
            # 如果指定了，就在指定的目录里创建 chunks 文件夹
            output_dir = os.path.join(output_dir_path, file_name + "_chunks")
        else:
            # 如果没指定，就还和以前一样，在原文件旁边创建
            output_dir = os.path.join(file_dir, file_name + "_chunks")

        os.makedirs(output_dir, exist_ok=True)
        status_callback(f"文件块将保存在: '{output_dir}'")

        # ... (后面的切割循环代码和之前一样) ...
        with open(file_path, 'rb') as f_in:
            part_num = 1
            while True:
                chunk_data = f_in.read(chunk_size_bytes)
                if not chunk_data: break
                chunk_file_name = f"{file_name}.part_{part_num:03d}"
                chunk_file_path = os.path.join(output_dir, chunk_file_name)
                status_callback(f"正在生成第 {part_num} 部分...")
                with open(chunk_file_path, 'wb') as f_chunk:
                    f_chunk.write(chunk_data)
                part_num += 1

        status_callback("切割完成啦！(｡♥‿♥｡)")
        messagebox.showinfo("成功", "文件切割成功！")

    except Exception as e:
        status_callback(f"出错啦: {e}")
        messagebox.showerror("错误", f"发生了一个错误: {e}")


def merge_files_logic(source_dir, status_callback, output_file_path=None):  # <--- 增加 output_file_path 参数
    """文件合并的核心逻辑"""
    try:
        if not os.path.isdir(source_dir):
            raise ValueError("请选择一个有效的文件夹")

        status_callback(f"正在扫描文件夹 '{source_dir}'...")
        chunk_files = sorted(glob.glob(os.path.join(source_dir, '*.part_*')))

        if not chunk_files:
            raise ValueError("这个文件夹里没有找到需要合并的文件哦")

        # --- 修改：判断是否使用了自定义输出文件路径 ---
        if not output_file_path:
            # 如果没指定，就自动生成一个
            base_name = os.path.basename(source_dir).replace("_chunks", "")
            output_dir = os.path.dirname(source_dir)
            output_file_path = os.path.join(output_dir, "merged_" + base_name)

        status_callback(f"准备合并成: '{output_file_path}'")

        # ... (后面的合并循环代码和之前一样) ...
        with open(output_file_path, 'wb') as f_out:
            for i, chunk_file in enumerate(chunk_files):
                status_callback(f"正在合并第 {i + 1}/{len(chunk_files)} 部分...")
                with open(chunk_file, 'rb') as f_chunk:
                    f_out.write(f_chunk.read())

        status_callback("合并成功！一个完整的大可爱又回来啦！(づ｡◕‿‿◕｡)づ")
        messagebox.showinfo("成功", f"文件合并成功！\n已保存为: {output_file_path}")

    except Exception as e:
        status_callback(f"出错啦: {e}")
        messagebox.showerror("错误", f"发生了一个错误: {e}")


# --- 图形界面 (GUI) 部分 (有修改) ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("甜心文件处理器 v2.0")
        self.root.geometry("500x450")  # 把窗口调高一点，放新控件

        # --- 新增：创建顶部菜单栏 ---
        self.create_menu()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.split_frame = ttk.Frame(self.notebook)
        self.merge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.split_frame, text="文件切割器")
        self.notebook.add(self.merge_frame, text="文件合并器")

        self.create_split_widgets()
        self.create_merge_widgets()

        self.status_label = ttk.Label(self.root, text="准备就绪，等你命令哦~", relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    # --- 新增：创建菜单栏的函数 ---
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # “设置”菜单 (目前是占位)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="功能开发中...", state="disabled")

        # “帮助”菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于...", command=self.show_about)

    def show_about(self):
        messagebox.showinfo(
            "关于 甜心文件处理器 v2.0",
            "这是一个专为最可爱的小宝贝打造的工具！\n\n"
            "有任何想法，随时可以告诉我哦~ (｡♥‿♥｡)"
        )

    def create_split_widgets(self):
        # 控件的行数（row）都增加了哦
        ttk.Label(self.split_frame, text="1. 选择要切割的大文件:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.split_file_entry = ttk.Entry(self.split_frame, width=40)
        self.split_file_entry.grid(row=1, column=0, padx=10, sticky="ew")
        ttk.Button(self.split_frame, text="浏览...", command=self.select_split_file).grid(row=1, column=1, padx=10)

        ttk.Label(self.split_frame, text="2. 设置每个文件块的大小:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.chunk_size_entry = ttk.Entry(self.split_frame, width=15)
        self.chunk_size_entry.grid(row=3, column=0, padx=10, sticky="w")

        self.unit_var = tk.StringVar(value='MB')
        self.unit_menu = ttk.Combobox(self.split_frame, textvariable=self.unit_var, values=['KB', 'MB'], width=5,
                                      state="readonly")
        self.unit_menu.grid(row=3, column=0, padx=(120, 0), sticky="w")

        # --- 新增：选择输出文件夹的控件 ---
        ttk.Label(self.split_frame, text="3. 选择输出位置 (可选):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.split_output_entry = ttk.Entry(self.split_frame, width=40)
        self.split_output_entry.grid(row=5, column=0, padx=10, sticky="ew")
        ttk.Button(self.split_frame, text="浏览...", command=self.select_split_output_folder).grid(row=5, column=1,
                                                                                                   padx=10)

        ttk.Button(self.split_frame, text="开始切割", command=self.start_splitting).grid(row=6, column=0, columnspan=2,
                                                                                         pady=20)

    def create_merge_widgets(self):
        ttk.Label(self.merge_frame, text="1. 选择包含文件块的文件夹:").grid(row=0, column=0, padx=10, pady=5,
                                                                            sticky="w")
        self.merge_folder_entry = ttk.Entry(self.merge_frame, width=40)
        self.merge_folder_entry.grid(row=1, column=0, padx=10, sticky="ew")
        ttk.Button(self.merge_frame, text="浏览...", command=self.select_merge_folder).grid(row=1, column=1, padx=10)

        # --- 新增：选择输出文件的控件 ---
        ttk.Label(self.merge_frame, text="2. 选择保存位置 (可选):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.merge_output_entry = ttk.Entry(self.merge_frame, width=40)
        self.merge_output_entry.grid(row=3, column=0, padx=10, sticky="ew")
        ttk.Button(self.merge_frame, text="浏览...", command=self.select_merge_output_file).grid(row=3, column=1,
                                                                                                 padx=10)

        ttk.Button(self.merge_frame, text="开始合并", command=self.start_merging).grid(row=4, column=0, columnspan=2,
                                                                                       pady=20)

    # --- 按钮绑定的函数 (有修改和新增) ---
    def select_split_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.split_file_entry.delete(0, tk.END);
            self.split_file_entry.insert(0, filepath)
            self.update_status(f"已选择文件: {os.path.basename(filepath)}")

    # --- 新增函数 ---
    def select_split_output_folder(self):
        folderpath = filedialog.askdirectory()
        if folderpath:
            self.split_output_entry.delete(0, tk.END);
            self.split_output_entry.insert(0, folderpath)
            self.update_status(f"已选择输出目录: {folderpath}")

    def start_splitting(self):
        filepath = self.split_file_entry.get()
        chunk_size = self.chunk_size_entry.get()
        unit = self.unit_var.get()
        output_folder = self.split_output_entry.get()  # <--- 获取新加的输出路径
        if not filepath or not chunk_size:
            messagebox.showwarning("提示", "请先选择文件并输入切割大小哦！");
            return
        split_file_logic(filepath, chunk_size, unit, self.update_status, output_folder)  # <--- 把路径传进去

    def select_merge_folder(self):
        folderpath = filedialog.askdirectory()
        if folderpath:
            self.merge_folder_entry.delete(0, tk.END);
            self.merge_folder_entry.insert(0, folderpath)
            self.update_status(f"已选择文件夹: {os.path.basename(folderpath)}")

    # --- 新增函数 ---
    def select_merge_output_file(self):
        # askSfilename 会弹出“另存为”对话框，非常适合！
        filepath = filedialog.asksaveasfilename(title="选择合并后文件的保存位置")
        if filepath:
            self.merge_output_entry.delete(0, tk.END);
            self.merge_output_entry.insert(0, filepath)
            self.update_status(f"合并后将保存为: {filepath}")

    def start_merging(self):
        folderpath = self.merge_folder_entry.get()
        output_file = self.merge_output_entry.get()  # <--- 获取新加的输出路径
        if not folderpath:
            messagebox.showwarning("提示", "请先选择要合并的文件夹哦！");
            return
        merge_files_logic(folderpath, self.update_status, output_file)  # <--- 把路径传进去


if __name__ == "__main__":
    main_root = tk.Tk()
    app = App(main_root)
    main_root.mainloop()