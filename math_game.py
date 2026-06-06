#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
三年级数学特训营 v4.0 正式版
LZH团队创作
快捷键: F1+B = 调试模式 | F2+B = 所有者模式
"""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import random
import json
import os
import hashlib
import sys
import traceback
import logging
import subprocess
from datetime import datetime
from functools import wraps

# ============== 全局常量 ==============
VERSION = "4.0.0"
BUILD_DATE = "2026-01-15"
TEAM_NAME = "LZH团队"

# 难度配置
DIFFICULTY_CONFIG = {
    "🌟 简单模式": {"min": 1, "max": 5, "name": "easy"},
    "⭐ 普通模式": {"min": 1, "max": 10, "name": "medium"},
    "🔥 困难模式": {"min": 1, "max": 20, "name": "hard"},
    "💀 专家模式": {"min": 1, "max": 50, "name": "expert"}
}

# ============== 日志系统 ==============
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f"math_game_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============== 异常处理装饰器 ==============
def safe_execute(default_return=None, error_message="操作失败"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                logger.error(traceback.format_exc())
                try:
                    if args and len(args) > 0 and hasattr(args[0], 'root'):
                        messagebox.showerror("系统提示", f"{error_message}\n\n错误已记录，程序将继续运行。")
                except:
                    pass
                return default_return
        return wrapper
    return decorator


class SecureConfig:
    """安全配置管理类"""
    
    def __init__(self):
        self.config_file = "config.dat"
    
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def verify_admin_password(self, password: str) -> bool:
        return self._hash(password) == self._hash("admin160910")
    
    def verify_card_key(self, card_key: str) -> bool:
        return self._hash(card_key) == self._hash("12345")
    
    def verify_owner_key(self, owner_key: str) -> bool:
        return self._hash(owner_key) == self._hash("cctv666")
    
    def load_config(self):
        default_config = {
            "total_questions": 5,
            "difficulty": "medium",
            "number_range": {"min": 1, "max": 10},
            "question_types": ["mixed", "brackets"],
            "show_steps": True,
            "auto_next_delay": {"correct": 1200, "wrong": 2000},
            "score_per_question": 1,
            "retry_on_wrong": True,
            "max_attempts_per_question": 2
        }
        
        if not os.path.exists(self.config_file):
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return default_config
    
    def _save_config(self, config: dict):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def update_difficulty(self, difficulty_name: str):
        """更新难度配置"""
        if difficulty_name in DIFFICULTY_CONFIG:
            config = DIFFICULTY_CONFIG[difficulty_name]
            self.config["difficulty"] = config["name"]
            self.config["number_range"] = {"min": config["min"], "max": config["max"]}
            self._save_config(self.config)
            return True
        return False


class OwnerPanel:
    """所有者面板 - 最高权限"""
    
    def __init__(self, parent, game_instance):
        self.parent = parent
        self.game = game_instance
        self.crash_count = 0
    
    def open_owner_panel(self):
        owner_window = tk.Toplevel(self.parent)
        owner_window.title("👑 所有者模式 - 最高权限控制台 👑")
        owner_window.geometry("900x800")
        owner_window.configure(bg='#1A1A2E')
        owner_window.resizable(True, True)
        
        title_frame = tk.Frame(owner_window, bg='#FF0000', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="👑 所有者模式 - 最高权限控制台 👑",
                 font=('微软雅黑', 18, 'bold'), bg='#FF0000', fg='white').pack(expand=True)
        
        warning_label = tk.Label(owner_window, 
            text="⚠️⚠️⚠️ 最高警告：所有者模式拥有系统级权限，可控制系统崩溃 ⚠️⚠️⚠️",
            font=('微软雅黑', 12, 'bold'), bg='#FF4444', fg='white', pady=8)
        warning_label.pack(fill='x', padx=20, pady=5)
        
        notebook = ttk.Notebook(owner_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 系统控制
        system_frame = tk.Frame(notebook, bg='#1A1A2E')
        notebook.add(system_frame, text="💀 系统控制")
        
        crash_frame = tk.LabelFrame(system_frame, text="💀 崩溃控制系统", 
                                     font=('微软雅黑', 12, 'bold'), bg='#1A1A2E', fg='#FF4444')
        crash_frame.pack(fill='x', padx=10, pady=10)
        tk.Label(crash_frame, text="警告：以下操作会导致程序崩溃！", 
                font=('微软雅黑', 11, 'bold'), bg='#1A1A2E', fg='#FF4444').pack(pady=5)
        
        btn_frame = tk.Frame(crash_frame, bg='#1A1A2E')
        btn_frame.pack(pady=10)
        
        def crash_by_error():
            self.crash_count += 1
            logger.warning(f"所有者触发崩溃 - 异常抛出, 次数: {self.crash_count}")
            raise Exception("所有者触发的系统崩溃")
        
        def crash_by_recursion():
            self.crash_count += 1
            logger.warning(f"所有者触发崩溃 - 递归溢出, 次数: {self.crash_count}")
            def recursive(n):
                return recursive(n + 1)
            recursive(0)
        
        def crash_by_memory():
            self.crash_count += 1
            logger.warning(f"所有者触发崩溃 - 内存溢出, 次数: {self.crash_count}")
            data = []
            while True:
                data.append([0] * 1000000)
        
        def crash_and_restart():
            self.crash_count += 1
            logger.warning(f"所有者触发崩溃 - 重启, 次数: {self.crash_count}")
            owner_window.destroy()
            self.parent.quit()
            self.parent.destroy()
            subprocess.Popen([sys.executable, sys.argv[0]])
            sys.exit(0)
        
        tk.Button(btn_frame, text="💥 异常抛出崩溃", command=crash_by_error,
                  font=('微软雅黑', 10, 'bold'), bg='#8B0000', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🌀 递归溢出崩溃", command=crash_by_recursion,
                  font=('微软雅黑', 10, 'bold'), bg='#8B0000', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="📈 内存溢出崩溃", command=crash_by_memory,
                  font=('微软雅黑', 10, 'bold'), bg='#8B0000', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🔄 崩溃并重启", command=crash_and_restart,
                  font=('微软雅黑', 10, 'bold'), bg='#FF4500', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        
        self.crash_label = tk.Label(crash_frame, text=f"已触发崩溃次数: {self.crash_count}",
                                     font=('微软雅黑', 10), bg='#1A1A2E', fg='#FF8888')
        self.crash_label.pack(pady=5)
        
        # 进程控制
        process_frame = tk.LabelFrame(system_frame, text="🔧 进程控制", 
                                       font=('微软雅黑', 12, 'bold'), bg='#1A1A2E', fg='#00FF00')
        process_frame.pack(fill='x', padx=10, pady=10)
        
        def kill_process():
            logger.warning("所有者触发 - 结束进程")
            os._exit(0)
        
        def restart_system():
            logger.warning("所有者触发 - 重启系统")
            owner_window.destroy()
            self.parent.quit()
            self.parent.destroy()
            subprocess.Popen([sys.executable, sys.argv[0]])
            sys.exit(0)
        
        def show_process_info():
            try:
                import psutil
                current_process = psutil.Process()
                info = f"PID: {current_process.pid}\n内存: {current_process.memory_info().rss / 1024 / 1024:.2f} MB\nCPU: {current_process.cpu_percent()}%\n线程: {current_process.num_threads()}"
                messagebox.showinfo("进程信息", info)
            except:
                messagebox.showinfo("进程信息", "请安装psutil: pip install psutil")
        
        btn_frame2 = tk.Frame(process_frame, bg='#1A1A2E')
        btn_frame2.pack(pady=10)
        tk.Button(btn_frame2, text="🔪 结束进程", command=kill_process,
                  font=('微软雅黑', 10, 'bold'), bg='#8B0000', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame2, text="🔄 重启程序", command=restart_system,
                  font=('微软雅黑', 10, 'bold'), bg='#FF4500', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame2, text="📊 进程信息", command=show_process_info,
                  font=('微软雅黑', 10, 'bold'), bg='#2196F3', fg='white', padx=15, pady=5).pack(side='left', padx=5)
        
        # 游戏控制
        game_frame = tk.Frame(notebook, bg='#1A1A2E')
        notebook.add(game_frame, text="🎮 游戏控制")
        
        state_frame = tk.LabelFrame(game_frame, text="🎮 游戏状态修改", 
                                     font=('微软雅黑', 12, 'bold'), bg='#1A1A2E', fg='#00FF00')
        state_frame.pack(fill='x', padx=10, pady=10)
        
        def set_score():
            new_score = simpledialog.askinteger("设置分数", "请输入新分数：", minvalue=0, maxvalue=9999)
            if new_score is not None:
                self.game.score = new_score
                max_score = self.game.config.get("score_per_question", 1) * self.game.total_questions
                self.game.score_label.config(text=f"{self.game.score} / {max_score}")
                messagebox.showinfo("成功", f"分数已设置为 {new_score}")
        
        def set_question():
            new_q = simpledialog.askinteger("跳转题目", f"请输入题目编号（1-{self.game.total_questions}）：", 
                                            minvalue=1, maxvalue=self.game.total_questions)
            if new_q:
                self.game.current_question = new_q
                self.game._next_question()
                messagebox.showinfo("成功", f"已跳转到第{new_q}题")
        
        def complete_game():
            self.game.current_question = self.game.total_questions + 1
            self.game._show_result()
        
        btn_frame_game = tk.Frame(state_frame, bg='#1A1A2E')
        btn_frame_game.pack(pady=10)
        tk.Button(btn_frame_game, text="💰 修改分数", command=set_score,
                  font=('微软雅黑', 10, 'bold'), bg='#4CAF50', fg='white', padx=10, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame_game, text="🎯 跳转题目", command=set_question,
                  font=('微软雅黑', 10, 'bold'), bg='#2196F3', fg='white', padx=10, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame_game, text="🏆 直接完成", command=complete_game,
                  font=('微软雅黑', 10, 'bold'), bg='#FF9800', fg='white', padx=10, pady=5).pack(side='left', padx=5)
        
        # 配置编辑
        config_frame = tk.Frame(notebook, bg='#1A1A2E')
        notebook.add(config_frame, text="⚙️ 配置编辑")
        
        config_edit_frame = tk.LabelFrame(config_frame, text="⚙️ 配置文件编辑", 
                                           font=('微软雅黑', 12, 'bold'), bg='#1A1A2E', fg='#00FF00')
        config_edit_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        config_text = tk.Text(config_edit_frame, font=('Consolas', 10), bg='#2D2D2D', fg='#D4D4D4', height=15)
        config_text.pack(fill='both', expand=True, padx=10, pady=10)
        config_text.insert('1.0', json.dumps(self.game.config, ensure_ascii=False, indent=2))
        
        def save_config():
            try:
                new_config = json.loads(config_text.get('1.0', tk.END))
                self.game.secure_config._save_config(new_config)
                self.game.config = new_config
                self.game.total_questions = new_config.get("total_questions", 5)
                messagebox.showinfo("成功", "配置已保存！游戏将重启")
                self.parent.quit()
                self.parent.destroy()
                subprocess.Popen([sys.executable, sys.argv[0]])
                sys.exit(0)
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")
        
        tk.Button(config_edit_frame, text="💾 保存配置并重启", command=save_config,
                  font=('微软雅黑', 11, 'bold'), bg='#4CAF50', fg='white', padx=20, pady=5).pack(pady=10)
        
        status_frame = tk.Frame(owner_window, bg='#1A1A2E', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        tk.Label(status_frame, text="所有者模式 - 最高权限 | 所有操作已记录到日志", 
                 font=('微软雅黑', 9), bg='#1A1A2E', fg='#888888').pack(expand=True)


class DebugPanel:
    """调试面板"""
    
    def __init__(self, parent, game_instance):
        self.parent = parent
        self.game = game_instance
        
    def open_debug_panel(self):
        debug_window = tk.Toplevel(self.parent)
        debug_window.title("🔧 调试模式 - 高权限控制台")
        debug_window.geometry("800x700")
        debug_window.configure(bg='#2C2C2C')
        debug_window.resizable(True, True)
        
        title_frame = tk.Frame(debug_window, bg='#FF8800', height=50)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🔧 调试模式 - 高权限控制台 🔧",
                 font=('微软雅黑', 16, 'bold'), bg='#FF8800', fg='white').pack(expand=True)
        
        notebook = ttk.Notebook(debug_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 代码查看器
        code_frame = tk.Frame(notebook, bg='#1E1E1E')
        notebook.add(code_frame, text="📝 代码查看器")
        code_text = tk.Text(code_frame, font=('Consolas', 10), bg='#2D2D2D', fg='#D4D4D4', wrap=tk.WORD)
        code_text.pack(fill='both', expand=True, padx=10, pady=10)
        try:
            with open(sys.argv[0], 'r', encoding='utf-8') as f:
                code_text.insert('1.0', f.read())
        except:
            code_text.insert('1.0', "无法读取代码")
        code_text.config(state='disabled')
        
        # 运行时变量
        vars_frame = tk.Frame(notebook, bg='#1E1E1E')
        notebook.add(vars_frame, text="📊 运行时变量")
        vars_text = tk.Text(vars_frame, font=('Consolas', 10), bg='#2D2D2D', fg='#D4D4D4', wrap=tk.WORD)
        vars_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        def refresh_vars():
            vars_text.delete('1.0', tk.END)
            info = f"当前题目：{self.game.current_question}/{self.game.total_questions}\n得分：{self.game.score}\n配置：{json.dumps(self.game.config, ensure_ascii=False, indent=2)}"
            vars_text.insert('1.0', info)
            vars_text.config(state='disabled')
        refresh_vars()
        tk.Button(vars_frame, text="🔄 刷新", command=refresh_vars,
                  font=('微软雅黑', 10), bg='#2196F3', fg='white', padx=15, pady=3).pack(pady=5)
        
        # 快速操作
        quick_frame = tk.Frame(notebook, bg='#1E1E1E')
        notebook.add(quick_frame, text="⚡ 快速操作")
        
        def add_score():
            self.game.score += 10
            max_score = self.game.config.get("score_per_question", 1) * self.game.total_questions
            self.game.score_label.config(text=f"{self.game.score} / {max_score}")
        
        def jump_to_question():
            q_num = simpledialog.askinteger("跳转", "请输入题目编号：", minvalue=1, maxvalue=self.game.total_questions)
            if q_num:
                self.game.current_question = q_num
                self.game._next_question()
        
        btn_frame = tk.Frame(quick_frame, bg='#1E1E1E')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="➕ 增加10分", command=add_score,
                  font=('微软雅黑', 11), bg='#4CAF50', fg='white', padx=15, pady=5).pack(pady=5)
        tk.Button(btn_frame, text="🎯 跳转题目", command=jump_to_question,
                  font=('微软雅黑', 11), bg='#2196F3', fg='white', padx=15, pady=5).pack(pady=5)
        tk.Button(btn_frame, text="🔄 重置游戏", command=self.game._restart_game,
                  font=('微软雅黑', 11), bg='#FF9800', fg='white', padx=15, pady=5).pack(pady=5)


class MathGame:
    """三年级数学特训营游戏主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"🧸 三年级数学特训营 v{VERSION} - {TEAM_NAME} 🧸")
        self.root.geometry("850x850")
        self.root.resizable(False, False)
        self.root.configure(bg='#F0F8FF')
        
        # 快捷键状态
        self.f1_pressed = False
        self.f2_pressed = False
        
        # 绑定快捷键
        self.root.bind('<F1>', self._on_f1_press)
        self.root.bind('<KeyRelease-F1>', self._on_f1_release)
        self.root.bind('<F2>', self._on_f2_press)
        self.root.bind('<KeyRelease-F2>', self._on_f2_release)
        self.root.bind('<KeyPress-b>', self._on_b_press)
        self.root.bind('<KeyPress-B>', self._on_b_press)
        
        self.secure_config = SecureConfig()
        
        if not self._verify_card_key_with_retry():
            self.root.destroy()
            sys.exit(0)
        
        self.config = self.secure_config.load_config()
        self.total_questions = self.config.get("total_questions", 5)
        self.current_question = 1
        self.score = 0
        self.current_answer = None
        self.current_step1 = ""
        self.current_step2 = ""
        self.waiting_for_retry = False
        self.attempts_on_current = 0
        self.max_attempts = self.config.get("max_attempts_per_question", 2)
        
        self._init_ui_components()
        self._create_widgets()
        self._next_question()
    
    def _on_f1_press(self, event):
        self.f1_pressed = True
        self.hint_label.config(text="🔧 调试模式待命中，请按 B 键", fg="#FF8800")
    
    def _on_f1_release(self, event):
        self.f1_pressed = False
        if not self.f2_pressed:
            self.hint_label.config(text="✨ 输入答案后点击提交或按回车键 ✨", fg="#8B0000")
    
    def _on_f2_press(self, event):
        self.f2_pressed = True
        self.hint_label.config(text="👑 所有者模式待命中，请按 B 键", fg="#FF0000")
    
    def _on_f2_release(self, event):
        self.f2_pressed = False
        if not self.f1_pressed:
            self.hint_label.config(text="✨ 输入答案后点击提交或按回车键 ✨", fg="#8B0000")
    
    def _on_b_press(self, event):
        if self.f1_pressed:
            self._activate_debug_mode()
            self.f1_pressed = False
        elif self.f2_pressed:
            self._activate_owner_mode()
            self.f2_pressed = False
    
    def _change_difficulty(self, event=None):
        """切换难度 - 普通用户可用"""
        selected = self.difficulty_var.get()
        if selected in DIFFICULTY_CONFIG:
            config = DIFFICULTY_CONFIG[selected]
            # 更新配置
            self.config["difficulty"] = config["name"]
            self.config["number_range"] = {"min": config["min"], "max": config["max"]}
            self.secure_config._save_config(self.config)
            
            # 更新显示
            diff_colors = {'easy': '#32CD32', 'medium': '#FFA500', 'hard': '#FF4500', 'expert': '#DC143C'}
            self.diff_badge.config(text=selected, bg=diff_colors.get(config["name"], '#FFA500'))
            
            # 提示用户
            messagebox.showinfo("难度已切换", f"已切换到{selected}\n数字范围：{config['min']} ~ {config['max']}\n下一题开始生效")
            
            logger.info(f"用户切换难度: {selected}")
    
    def _activate_debug_mode(self):
        """激活调试模式 - 需要管理员密码和卡密"""
        verify_window = tk.Toplevel(self.root)
        verify_window.title("调试模式验证")
        verify_window.geometry("420x350")
        verify_window.configure(bg='#F0F8FF')
        verify_window.resizable(False, False)
        verify_window.transient(self.root)
        verify_window.grab_set()
        
        title_frame = tk.Frame(verify_window, bg='#FF8800', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🔧 调试模式验证 🔧",
                 font=('微软雅黑', 16, 'bold'), bg='#FF8800', fg='white').pack(expand=True)
        
        tk.Label(verify_window, text="请输入管理员密码和卡密",
                 font=('微软雅黑', 11), bg='#F0F8FF', fg='#333333').pack(pady=(20, 10))
        
        tk.Label(verify_window, text="管理员密码：", font=('微软雅黑', 10), bg='#F0F8FF').pack()
        pwd_entry = tk.Entry(verify_window, font=('微软雅黑', 12), width=20, show="*", justify='center')
        pwd_entry.pack(pady=5)
        
        tk.Label(verify_window, text="卡密：", font=('微软雅黑', 10), bg='#F0F8FF').pack(pady=(10, 0))
        card_entry = tk.Entry(verify_window, font=('微软雅黑', 12), width=20, show="*", justify='center')
        card_entry.pack(pady=5)
        
        msg_label = tk.Label(verify_window, text="", font=('微软雅黑', 10), bg='#F0F8FF', fg='red')
        msg_label.pack(pady=10)
        
        def verify():
            if (self.secure_config.verify_admin_password(pwd_entry.get()) and 
                self.secure_config.verify_card_key(card_entry.get())):
                verify_window.destroy()
                logger.info("调试模式已激活")
                DebugPanel(self.root, self).open_debug_panel()
            else:
                msg_label.config(text="❌ 验证失败！")
                pwd_entry.delete(0, tk.END)
                card_entry.delete(0, tk.END)
        
        btn_frame = tk.Frame(verify_window, bg='#F0F8FF')
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="进入调试模式", command=verify,
                  font=('微软雅黑', 11, 'bold'), bg='#FF8800', fg='white', padx=20, pady=6).pack(side='left', padx=10)
        tk.Button(btn_frame, text="取消", command=verify_window.destroy,
                  font=('微软雅黑', 11), bg='#6C757D', fg='white', padx=20, pady=6).pack(side='left', padx=10)
        
        pwd_entry.bind('<Return>', lambda e: verify())
        card_entry.bind('<Return>', lambda e: verify())
    
    def _activate_owner_mode(self):
        """激活所有者模式 - 需要三重验证"""
        verify_window = tk.Toplevel(self.root)
        verify_window.title("所有者模式验证")
        verify_window.geometry("450x480")
        verify_window.configure(bg='#1A1A2E')
        verify_window.resizable(False, False)
        verify_window.transient(self.root)
        verify_window.grab_set()
        
        title_frame = tk.Frame(verify_window, bg='#FF0000', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="👑 所有者模式验证 👑",
                 font=('微软雅黑', 16, 'bold'), bg='#FF0000', fg='white').pack(expand=True)
        
        tk.Label(verify_window, text="⚠️ 最高权限验证 - 需要三重验证 ⚠️",
                 font=('微软雅黑', 11, 'bold'), bg='#1A1A2E', fg='#FF8888').pack(pady=(20, 10))
        
        tk.Label(verify_window, text="所有者密码：", font=('微软雅黑', 10), bg='#1A1A2E', fg='white').pack()
        owner_entry = tk.Entry(verify_window, font=('微软雅黑', 12), width=25, show="*", justify='center')
        owner_entry.pack(pady=5)
        
        tk.Label(verify_window, text="管理员密码：", font=('微软雅黑', 10), bg='#1A1A2E', fg='white').pack(pady=(10, 0))
        pwd_entry = tk.Entry(verify_window, font=('微软雅黑', 12), width=25, show="*", justify='center')
        pwd_entry.pack(pady=5)
        
        tk.Label(verify_window, text="卡密：", font=('微软雅黑', 10), bg='#1A1A2E', fg='white').pack(pady=(10, 0))
        card_entry = tk.Entry(verify_window, font=('微软雅黑', 12), width=25, show="*", justify='center')
        card_entry.pack(pady=5)
        
        msg_label = tk.Label(verify_window, text="", font=('微软雅黑', 10), bg='#1A1A2E', fg='red')
        msg_label.pack(pady=10)
        
        def verify():
            if (self.secure_config.verify_owner_key(owner_entry.get()) and 
                self.secure_config.verify_admin_password(pwd_entry.get()) and 
                self.secure_config.verify_card_key(card_entry.get())):
                verify_window.destroy()
                logger.warning("所有者模式已激活 - 最高权限")
                OwnerPanel(self.root, self).open_owner_panel()
            else:
                msg_label.config(text="❌ 验证失败！请检查所有密码")
                owner_entry.delete(0, tk.END)
                pwd_entry.delete(0, tk.END)
                card_entry.delete(0, tk.END)
                owner_entry.focus()
        
        btn_frame = tk.Frame(verify_window, bg='#1A1A2E')
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="进入所有者模式", command=verify,
                  font=('微软雅黑', 11, 'bold'), bg='#FF0000', fg='white', padx=20, pady=6).pack(side='left', padx=10)
        tk.Button(btn_frame, text="取消", command=verify_window.destroy,
                  font=('微软雅黑', 11), bg='#6C757D', fg='white', padx=20, pady=6).pack(side='left', padx=10)
        
        owner_entry.bind('<Return>', lambda e: verify())
        pwd_entry.bind('<Return>', lambda e: verify())
        card_entry.bind('<Return>', lambda e: verify())
    
    def _init_ui_components(self):
        self.score_label = None
        self.progress_label = None
        self.diff_badge = None
        self.question_label = None
        self.entry_var = None
        self.entry = None
        self.hint_label = None
        self.step_label = None
        self.submit_btn = None
        self.difficulty_var = None
    
    @safe_execute(default_return=False)
    def _verify_card_key_with_retry(self) -> bool:
        for attempt in range(3):
            if self._verify_card_key_dialog(attempt + 1, 3):
                return True
        messagebox.showerror("验证失败", "验证错误次数过多！程序将退出。")
        return False
    
    @safe_execute(default_return=False)
    def _verify_card_key_dialog(self, attempt: int, max_attempts: int) -> bool:
        verify_window = tk.Toplevel(self.root)
        verify_window.title("身份验证")
        verify_window.geometry("400x300")
        verify_window.configure(bg='#F0F8FF')
        verify_window.resizable(False, False)
        verify_window.transient(self.root)
        verify_window.grab_set()
        
        title_frame = tk.Frame(verify_window, bg='#FFD700', height=70)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🔐 身份验证 🔐",
                 font=('微软雅黑', 18, 'bold'), bg='#FFD700', fg='#8B4513').pack(expand=True)
        
        tk.Label(verify_window, text=f"请验证身份（第{attempt}/{max_attempts}次尝试）",
                 font=('微软雅黑', 11), bg='#F0F8FF', fg='#333333').pack(pady=(30, 15))
        
        entry = tk.Entry(verify_window, font=('微软雅黑', 14), width=20, show="*", justify='center')
        entry.pack(pady=10)
        entry.focus()
        
        msg = tk.Label(verify_window, text="", font=('微软雅黑', 10), bg='#F0F8FF', fg='red')
        msg.pack(pady=5)
        
        result = [False]
        
        def verify():
            if self.secure_config.verify_card_key(entry.get().strip()):
                result[0] = True
                verify_window.destroy()
            else:
                remaining = max_attempts - attempt
                if remaining > 0:
                    msg.config(text=f"❌ 验证失败！还剩{remaining}次机会")
                    entry.delete(0, tk.END)
                    entry.focus()
        
        btn_frame = tk.Frame(verify_window, bg='#F0F8FF')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="确认", command=verify,
                  font=('微软雅黑', 11, 'bold'), bg='#4CAF50', fg='white', padx=25, pady=6).pack(side='left', padx=10)
        tk.Button(btn_frame, text="退出", command=verify_window.destroy,
                  font=('微软雅黑', 11), bg='#f44336', fg='white', padx=25, pady=6).pack(side='left', padx=10)
        entry.bind('<Return>', lambda e: verify())
        
        self.root.wait_window(verify_window)
        return result[0]
    
    @safe_execute()
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎮 游戏", menu=game_menu)
        game_menu.add_command(label="重新开始", command=self._restart_game)
        game_menu.add_separator()
        game_menu.add_command(label="退出游戏", command=self._quit_game)
        
        admin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👑 管理员", menu=admin_menu)
        admin_menu.add_command(label="登录控制台", command=self._show_admin_login)
        admin_menu.add_separator()
        admin_menu.add_command(label="更新日志", command=self._show_changelog)
        admin_menu.add_command(label="帮助文档", command=self._show_help)
        admin_menu.add_command(label="关于软件", command=self._show_about)
    
    def _quit_game(self):
        if messagebox.askyesno("确认退出", "确定要退出游戏吗？"):
            self.root.quit()
    
    @safe_execute()
    def _show_admin_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("管理员登录")
        login_window.geometry("400x280")
        login_window.configure(bg='#F0F8FF')
        login_window.resizable(False, False)
        login_window.transient(self.root)
        login_window.grab_set()
        
        title_frame = tk.Frame(login_window, bg='#FFD700', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="👑 管理员登录 👑",
                 font=('微软雅黑', 16, 'bold'), bg='#FFD700', fg='#8B4513').pack(expand=True)
        
        tk.Label(login_window, text="请输入管理员密码：",
                 font=('微软雅黑', 11), bg='#F0F8FF', fg='#333333').pack(pady=25)
        
        entry = tk.Entry(login_window, font=('微软雅黑', 14), width=20, show="*", justify='center')
        entry.pack(pady=10)
        entry.focus()
        
        msg = tk.Label(login_window, text="", font=('微软雅黑', 10), bg='#F0F8FF', fg='red')
        msg.pack(pady=5)
        
        attempts = [3]
        
        def verify():
            if self.secure_config.verify_admin_password(entry.get()):
                login_window.destroy()
                self._open_admin_panel()
            else:
                attempts[0] -= 1
                if attempts[0] <= 0:
                    messagebox.showerror("验证失败", "密码错误次数过多！")
                    login_window.destroy()
                else:
                    msg.config(text=f"❌ 密码错误！还剩{attempts[0]}次机会")
                    entry.delete(0, tk.END)
                    entry.focus()
        
        btn_frame = tk.Frame(login_window, bg='#F0F8FF')
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="确认", command=verify,
                  font=('微软雅黑', 11, 'bold'), bg='#4CAF50', fg='white', padx=20, pady=5).pack(side='left', padx=10)
        tk.Button(btn_frame, text="取消", command=login_window.destroy,
                  font=('微软雅黑', 11), bg='#6C757D', fg='white', padx=20, pady=5).pack(side='left', padx=10)
        entry.bind('<Return>', lambda e: verify())
    
    @safe_execute()
    def _open_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("管理员控制面板")
        admin_window.geometry("650x750")
        admin_window.configure(bg='#F0F8FF')
        admin_window.resizable(False, False)
        
        title_frame = tk.Frame(admin_window, bg='#FFD700', height=50)
        title_frame.pack(fill='x', pady=(0, 15))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="👑 管理员控制面板 👑",
                 font=('微软雅黑', 16, 'bold'), bg='#FFD700', fg='#8B4513').pack(expand=True)
        
        main_frame = tk.Frame(admin_window, bg='#F0F8FF')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame, bg='#F0F8FF', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F0F8FF')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        config_frame = tk.LabelFrame(scrollable_frame, text="📋 当前配置", font=('微软雅黑', 12, 'bold'), bg='#F0F8FF')
        config_frame.pack(fill='x', pady=5)
        config_text = tk.Text(config_frame, height=8, font=('微软雅黑', 9), bg='#FFFFFF', wrap=tk.WORD)
        config_text.pack(fill='x', padx=10, pady=5)
        config_text.insert('1.0', json.dumps(self.config, ensure_ascii=False, indent=2))
        config_text.config(state='disabled')
        
        modify_frame = tk.LabelFrame(scrollable_frame, text="✏️ 系统设置", font=('微软雅黑', 12, 'bold'), bg='#F0F8FF')
        modify_frame.pack(fill='x', pady=10)
        
        row = 0
        tk.Label(modify_frame, text="题目数量 (1-50):", font=('微软雅黑', 10), bg='#F0F8FF').grid(row=row, column=0, sticky='w', pady=8, padx=10)
        q_var = tk.IntVar(value=self.config.get('total_questions', 5))
        tk.Spinbox(modify_frame, from_=1, to=50, textvariable=q_var, width=15).grid(row=row, column=1, pady=8, padx=10)
        
        row += 1
        tk.Label(modify_frame, text="每题分数 (1-10):", font=('微软雅黑', 10), bg='#F0F8FF').grid(row=row, column=0, sticky='w', pady=8, padx=10)
        s_var = tk.IntVar(value=self.config.get('score_per_question', 1))
        tk.Spinbox(modify_frame, from_=1, to=10, textvariable=s_var, width=15).grid(row=row, column=1, pady=8, padx=10)
        
        row += 1
        tk.Label(modify_frame, text="每题最大尝试次数:", font=('微软雅黑', 10), bg='#F0F8FF').grid(row=row, column=0, sticky='w', pady=8, padx=10)
        m_var = tk.IntVar(value=self.config.get('max_attempts_per_question', 2))
        tk.Spinbox(modify_frame, from_=1, to=5, textvariable=m_var, width=15).grid(row=row, column=1, pady=8, padx=10)
        
        row += 1
        tk.Label(modify_frame, text="题型选择:", font=('微软雅黑', 10), bg='#F0F8FF').grid(row=row, column=0, sticky='w', pady=8, padx=10)
        mixed_var = tk.BooleanVar(value='mixed' in self.config.get('question_types', ['mixed', 'brackets']))
        brackets_var = tk.BooleanVar(value='brackets' in self.config.get('question_types', ['mixed', 'brackets']))
        tk.Checkbutton(modify_frame, text="混合运算 (a + b × c)", variable=mixed_var, bg='#F0F8FF').grid(row=row, column=1, sticky='w')
        
        row += 1
        tk.Checkbutton(modify_frame, text="括号运算 ((a + b) × c)", variable=brackets_var, bg='#F0F8FF').grid(row=row, column=1, sticky='w')
        
        row += 1
        tk.Label(modify_frame, text="其他设置:", font=('微软雅黑', 10), bg='#F0F8FF').grid(row=row, column=0, sticky='w', pady=8, padx=10)
        retry_var = tk.BooleanVar(value=self.config.get('retry_on_wrong', True))
        tk.Checkbutton(modify_frame, text="答错后允许重试", variable=retry_var, bg='#F0F8FF').grid(row=row, column=1, sticky='w')
        
        row += 1
        steps_var = tk.BooleanVar(value=self.config.get('show_steps', True))
        tk.Checkbutton(modify_frame, text="显示计算步骤", variable=steps_var, bg='#F0F8FF').grid(row=row, column=1, sticky='w')
        
        def save_and_restart():
            new_config = {
                "total_questions": q_var.get(),
                "difficulty": self.config.get("difficulty", "medium"),
                "number_range": self.config.get("number_range", {"min": 1, "max": 10}),
                "question_types": [],
                "show_steps": steps_var.get(),
                "auto_next_delay": self.config.get("auto_next_delay", {"correct": 1200, "wrong": 2000}),
                "score_per_question": s_var.get(),
                "retry_on_wrong": retry_var.get(),
                "max_attempts_per_question": m_var.get()
            }
            if mixed_var.get():
                new_config["question_types"].append("mixed")
            if brackets_var.get():
                new_config["question_types"].append("brackets")
            if not new_config["question_types"]:
                messagebox.showwarning("警告", "至少选择一种题型！")
                return
            self.secure_config._save_config(new_config)
            messagebox.showinfo("成功", "配置已保存！游戏将重启。")
            admin_window.destroy()
            self.root.quit()
            self.root.destroy()
            new_root = tk.Tk()
            MathGame(new_root)
            new_root.mainloop()
        
        btn_frame = tk.Frame(scrollable_frame, bg='#F0F8FF')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="💾 保存并重启", command=save_and_restart,
                  font=('微软雅黑', 11, 'bold'), bg='#4CAF50', fg='white', padx=20, pady=8).pack(side='left', padx=10)
        tk.Button(btn_frame, text="❌ 关闭", command=admin_window.destroy,
                  font=('微软雅黑', 11), bg='#6C757D', fg='white', padx=20, pady=8).pack(side='left', padx=10)
    
    @safe_execute()
    def _create_widgets(self):
        self._create_menu()
        
        title_frame = tk.Frame(self.root, bg='#FFD700', height=80)
        title_frame.pack(fill='x', pady=(0, 15))
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text=f"🧸 三年级数学特训营 v{VERSION} 🧸",
                 font=('微软雅黑', 22, 'bold'), bg='#FFD700', fg='#8B4513').pack(expand=True)
        
        tk.Label(self.root, text=f"© {TEAM_NAME} | 专业版",
                 font=('微软雅黑', 10), bg='#F0F8FF', fg='#999999').pack(pady=(0, 10))
        
        info_frame = tk.Frame(self.root, bg='#F0F8FF', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        score_per_q = self.config.get('score_per_question', 1)
        max_score = score_per_q * self.total_questions
        
        score_frame = tk.Frame(info_frame, bg='#F0F8FF')
        score_frame.pack(side='left', padx=20, pady=10)
        tk.Label(score_frame, text="当前得分", font=('微软雅黑', 11), bg='#F0F8FF', fg='#666').pack()
        self.score_label = tk.Label(score_frame, text=f"0 / {max_score}",
                                     font=('微软雅黑', 20, 'bold'), bg='#F0F8FF', fg='#FF6347')
        self.score_label.pack()
        
        progress_frame = tk.Frame(info_frame, bg='#F0F8FF')
        progress_frame.pack(side='left', padx=40, pady=10)
        tk.Label(progress_frame, text="题目进度", font=('微软雅黑', 11), bg='#F0F8FF', fg='#666').pack()
        self.progress_label = tk.Label(progress_frame, text=f"第 1 / {self.total_questions} 题",
                                        font=('微软雅黑', 16, 'bold'), bg='#F0F8FF', fg='#2E8B57')
        self.progress_label.pack()
        
        # 难度选择区域（普通用户可用）
        diff_frame = tk.Frame(info_frame, bg='#F0F8FF')
        diff_frame.pack(side='right', padx=20, pady=10)
        
        tk.Label(diff_frame, text="难度选择：", font=('微软雅黑', 11), bg='#F0F8FF', fg='#666').pack(side='left')
        
        # 获取当前难度对应的显示文本
        current_diff = self.config.get('difficulty', 'medium')
        current_display = "⭐ 普通模式"
        for display, conf in DIFFICULTY_CONFIG.items():
            if conf["name"] == current_diff:
                current_display = display
                break
        
        self.difficulty_var = tk.StringVar(value=current_display)
        diff_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty_var, 
                                   values=list(DIFFICULTY_CONFIG.keys()), width=12, state="readonly")
        diff_combo.pack(side='left', padx=10)
        diff_combo.bind('<<ComboboxSelected>>', self._change_difficulty)
        
        # 难度徽章（保留用于显示）
        diff_colors = {'easy': '#32CD32', 'medium': '#FFA500', 'hard': '#FF4500', 'expert': '#DC143C'}
        self.diff_badge = tk.Label(diff_frame, text=current_display,
                                    font=('微软雅黑', 10, 'bold'), bg=diff_colors.get(current_diff, '#FFA500'),
                                    fg='white', padx=10, pady=3)
        self.diff_badge.pack(side='left', padx=5)
        
        question_card = tk.Frame(self.root, bg='#FFFFFF', relief='ridge', bd=3)
        question_card.pack(pady=20, padx=40, fill='x')
        self.question_label = tk.Label(question_card, text="加载中...",
                                        font=('微软雅黑', 32, 'bold'), bg='#FFFFFF', fg='#1E3A8A', height=2)
        self.question_label.pack(pady=40)
        
        input_frame = tk.Frame(self.root, bg='#F0F8FF')
        input_frame.pack(pady=20)
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(input_frame, textvariable=self.entry_var, font=('微软雅黑', 20),
                               width=12, justify='center', bd=3, relief='ridge')
        self.entry.pack(side='left', padx=15)
        self.entry.bind('<Return>', lambda event: self._check_answer())
        self.submit_btn = tk.Button(input_frame, text="✓ 提交答案 ✓", command=self._check_answer,
                                     font=('微软雅黑', 14, 'bold'), bg='#4CAF50', fg='white', padx=25, pady=8)
        self.submit_btn.pack(side='left', padx=15)
        
        self.hint_label = tk.Label(self.root, text="✨ 输入答案后点击提交或按回车键 ✨",
                                    font=('微软雅黑', 11), bg='#FFFACD', fg='#8B0000',
                                    wraplength=600, relief='sunken', bd=2, padx=15, pady=12)
        self.hint_label.pack(pady=15, padx=40, fill='x')
        
        if self.config.get("show_steps", True):
            self.step_label = tk.Label(self.root, text="📖 答题后将显示详细计算步骤",
                                        font=('微软雅黑', 10), bg='#E6E6FA', fg='#4B0082',
                                        wraplength=600, relief='groove', bd=2, padx=15, pady=10)
            self.step_label.pack(pady=10, padx=40, fill='x')
        
        control_frame = tk.Frame(self.root, bg='#F0F8FF')
        control_frame.pack(pady=20)
        tk.Button(control_frame, text="🔄 重新开始", command=self._restart_game,
                  font=('微软雅黑', 11), bg='#6C757D', fg='white', padx=25, pady=6).pack(side='left', padx=15)
        
        footer_frame = tk.Frame(self.root, bg='#F0F8FF')
        footer_frame.pack(side='bottom', fill='x', pady=10)
        tk.Label(footer_frame, text=f"© 2026 {TEAM_NAME} | 正式版 v{VERSION} | F1+B=调试模式 | F2+B=所有者模式",
                 font=('微软雅黑', 9), bg='#F0F8FF', fg='#999999').pack()
    
    @safe_execute()
    def _generate_question(self):
        r = self.config.get("number_range", {"min": 1, "max": 10})
        a = random.randint(r["min"], r["max"])
        b = random.randint(r["min"], r["max"])
        c = random.randint(r["min"], r["max"])
        types = self.config.get("question_types", ["mixed", "brackets"])
        if random.choice(types) == 'mixed':
            answer = a + b * c
            return f"{a} + {b} × {c}", answer, f"① 先算乘法：{b} × {c} = {b*c}", f"② 再算加法：{a} + {b*c} = {answer}"
        else:
            answer = (a + b) * c
            return f"({a} + {b}) × {c}", answer, f"① 先算括号：{a} + {b} = {a+b}", f"② 再算乘法：{a+b} × {c} = {answer}"
    
    @safe_execute()
    def _next_question(self):
        if self.current_question > self.total_questions:
            self._show_result()
            return
        self.waiting_for_retry = False
        self.attempts_on_current = 0
        self.entry_var.set("")
        self.hint_label.config(text="✨ 输入答案后点击提交或按回车键 ✨", fg="#8B0000")
        if hasattr(self, 'step_label') and self.step_label:
            self.step_label.config(text="📖 答题后将显示详细计算步骤")
        q, ans, s1, s2 = self._generate_question()
        self.current_answer = ans
        self.current_step1 = s1
        self.current_step2 = s2
        self.question_label.config(text=f"{q} = ?")
        self.progress_label.config(text=f"第 {self.current_question} / {self.total_questions} 题")
        self.submit_btn.config(state='normal', bg='#4CAF50')
        self.entry.config(state='normal')
        self.entry.focus()
    
    @safe_execute()
    def _check_answer(self):
        try:
            ans = self.entry_var.get().strip()
            if not ans:
                self.hint_label.config(text="⚠️ 请输入答案！", fg="#FF4500")
                return
            num = int(ans)
            self.attempts_on_current += 1
            if num == self.current_answer:
                if not self.waiting_for_retry:
                    spq = self.config.get("score_per_question", 1)
                    self.score += spq
                    max_score = spq * self.total_questions
                    self.score_label.config(text=f"{self.score} / {max_score}")
                    self.hint_label.config(text=f"✅ 正确！ +{spq}分", fg="#006400")
                else:
                    self.hint_label.config(text="✅ 正确！继续加油！", fg="#006400")
                if hasattr(self, 'step_label') and self.step_label:
                    self.step_label.config(text=f"📖 {self.current_step1}\n   {self.current_step2}")
                self.submit_btn.config(state='disabled', bg='#9E9E9E')
                self.entry.config(state='disabled')
                delay = self.config.get("auto_next_delay", {"correct": 1200}).get("correct", 1200)
                self.root.after(delay, self._advance_question)
            else:
                max_att = self.config.get("max_attempts_per_question", 2)
                if self.attempts_on_current < max_att and self.config.get("retry_on_wrong", True):
                    remaining = max_att - self.attempts_on_current
                    messagebox.showinfo("提示", f"正确答案是 {self.current_answer}\n还有 {remaining} 次机会")
                    self.hint_label.config(text=f"❌ 再试试！", fg="#FF8C00")
                    self.entry_var.set("")
                    self.entry.focus()
                    self.waiting_for_retry = True
                else:
                    messagebox.showinfo("提示", f"正确答案是 {self.current_answer}\n继续下一题！")
                    self.hint_label.config(text=f"❌ 正确答案：{self.current_answer}", fg="#8B0000")
                    if hasattr(self, 'step_label') and self.step_label:
                        self.step_label.config(text=f"📖 {self.current_step1}\n   {self.current_step2}")
                    self.submit_btn.config(state='disabled', bg='#9E9E9E')
                    self.entry.config(state='disabled')
                    delay = self.config.get("auto_next_delay", {"wrong": 2000}).get("wrong", 2000)
                    self.root.after(delay, self._advance_question)
        except ValueError:
            self.hint_label.config(text="⚠️ 请输入数字！", fg="#FF4500")
    
    @safe_execute()
    def _advance_question(self):
        self.current_question += 1
        self._next_question()
    
    @safe_execute()
    def _show_result(self):
        spq = self.config.get("score_per_question", 1)
        max_score = spq * self.total_questions
        pct = (self.score / max_score) * 100 if max_score > 0 else 0
        if pct == 100:
            comment = "🏆 完美！"
        elif pct >= 80:
            comment = "🎉 优秀！"
        elif pct >= 60:
            comment = "📚 不错！"
        else:
            comment = "💪 加油！"
        msg = f"完成：{self.current_question-1}/{self.total_questions}\n得分：{self.score}/{max_score}\n正确率：{pct:.1f}%\n\n{comment}"
        messagebox.showinfo("游戏结束", msg)
        if messagebox.askyesno("再来一局", "是否重新开始？"):
            self._restart_game()
        else:
            self.root.quit()
    
    @safe_execute()
    def _restart_game(self):
        self.current_question = 1
        self.score = 0
        self.waiting_for_retry = False
        self.attempts_on_current = 0
        spq = self.config.get("score_per_question", 1)
        max_score = spq * self.total_questions
        self.score_label.config(text=f"0 / {max_score}")
        self._next_question()
    
    @safe_execute()
    def _show_changelog(self):
        text = f"""更新日志 v{VERSION}

【Version 4.0】- {BUILD_DATE}

✨ 核心功能：
   • 三年级数学混合运算练习
   • 可配置题目数量、难度、分数
   • 普通用户可直接切换难度

🛡️ 安全特性：
   • SHA-256 加密
   • 三重验证机制

🔧 隐藏模式：
   • 调试模式：F1+B（需密码+卡密）
   • 所有者模式：F2+B（需三重验证）

📋 密码：
   • 卡密：12345
   • 管理员：admin160910
   • 所有者：cctv666

难度说明：
   • 简单模式：数字1-5
   • 普通模式：数字1-10
   • 困难模式：数字1-20
   • 专家模式：数字1-50

© {TEAM_NAME}"""
        messagebox.showinfo("更新日志", text)
    
    @safe_execute()
    def _show_help(self):
        text = f"""帮助文档 v{VERSION}

【快捷键】
• F1+B - 调试模式（需密码+卡密）
• F2+B - 所有者模式（需三重验证）

【难度选择】
• 游戏界面右侧可直接选择难度
• 简单模式：1-5
• 普通模式：1-10
• 困难模式：1-20
• 专家模式：1-50

【游戏规则】
• 先乘除后加减，有括号先算括号
• 每题有2次尝试机会

© {TEAM_NAME}"""
        messagebox.showinfo("帮助", text)
    
    @safe_execute()
    def _show_about(self):
        text = f"""三年级数学特训营 v{VERSION}

版本：{VERSION}
开发：{TEAM_NAME}

密码：
• 卡密：12345
• 管理员：admin160910
• 所有者：cctv666

© 2026 {TEAM_NAME}"""
        messagebox.showinfo("关于", text)


def main():
    try:
        root = tk.Tk()
        MathGame(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"崩溃: {e}")
        messagebox.showerror("错误", f"程序崩溃：{e}\n日志：{LOG_FILE}")
        sys.exit(1)


if __name__ == "__main__":
    main()