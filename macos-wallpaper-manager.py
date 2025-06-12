#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS 动态壁纸批量下载器
Copyright (c) 2025 Xiangjigong. 保留所有权利.

本工具用于管理macOS系统动态壁纸，支持按分类下载/删除4K SDR 240FPS壁纸。

本程序是自由软件，你可以根据自由软件基金会发布的GNU通用公共许可证第三版或（根据你的选择）任何更高版本
重新发布它和/或修改它。我们希望本程序有用，但不提供任何担保，甚至不保证适销性或适合特定用途的担保。

项目主页：https://github.com/xiangjigong/macos-wallpaper-manager
问题反馈：https://github.com/xiangjigong/macos-wallpaper-manager/issues
联系邮箱：xiangjigong@qq.com
"""
import http.client
import json
import os
import plistlib
import shutil
import ssl
import time
import urllib.parse
from multiprocessing.pool import ThreadPool
from threading import Lock

# 系统路径常量
IDLEASSETSD_PATH = "/Library/Application Support/com.apple.idleassetsd"
STRINGS_PATH = os.path.join(IDLEASSETSD_PATH, "Customer/TVIdleScreenStrings.bundle/en.lproj/Localizable.nocache.strings")
ENTRIES_PATH = os.path.join(IDLEASSETSD_PATH, "Customer/entries.json")
VIDEO_PATH = os.path.join(IDLEASSETSD_PATH, "Customer/4KSDR240FPS")

class WallpaperManager:
    def __init__(self):
        self.strings = {}
        self.assets = []
        self.categories = []
        self.lock = Lock()
        
    def load_data(self):
        """加载壁纸元数据"""
        try:
            with open(STRINGS_PATH, "rb") as fp:
                self.strings = plistlib.load(fp)
            with open(ENTRIES_PATH, "r") as fp:
                data = json.load(fp)
                self.assets = data.get("assets", [])
                self.categories = data.get("categories", [])
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            exit(1)
    
    def get_category_name(self, category):
        """获取分类名称"""
        return self.strings.get(category.get("localizedNameKey", ""), "")
    
    def get_asset_name(self, asset):
        """获取壁纸名称"""
        return self.strings.get(asset.get("localizedNameKey", ""), "")
    
    def get_assets_by_category(self, category_id=None):
        """获取指定分类的壁纸列表"""
        result = []
        for asset in self.assets:
            if category_id and category_id not in asset.get("categories", []):
                continue
            
            name = self.get_asset_name(asset)
            asset_id = asset.get("id", "")
            url = asset.get("url-4K-SDR-240FPS", "")
            
            if not name or not asset_id or not url:
                continue
            
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1]
            dest_path = os.path.join(VIDEO_PATH, f"{asset_id}{ext}")
            result.append((name, url, dest_path))
        
        return result
    
    def get_file_size(self, url):
        """获取远程文件大小"""
        parsed = urllib.parse.urlparse(url)
        context = ssl._create_unverified_context()
        
        try:
            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(parsed.netloc, context=context)
            else:
                conn = http.client.HTTPConnection(parsed.netloc)
            
            conn.request("HEAD", parsed.path)
            resp = conn.getresponse()
            return int(resp.getheader("Content-Length", 0))
        except Exception as e:
            print(f"获取文件大小失败: {str(e)}")
            return 0
        finally:
            conn.close()
    
    def download_asset(self, asset_info, tracker):
        """下载单个壁纸文件"""
        name, url, dest_path = asset_info
        parsed = urllib.parse.urlparse(url)
        context = ssl._create_unverified_context()
        
        try:
            file_size = self.get_file_size(url)
            
            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(parsed.netloc, context=context)
            else:
                conn = http.client.HTTPConnection(parsed.netloc)
            
            conn.request("GET", parsed.path)
            resp = conn.getresponse()
            
            if resp.status == 200:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, "wb") as f:
                    shutil.copyfileobj(resp, f)
                
                with self.lock:
                    tracker.update(file_size)
                return f"✓ {name}"
            return f"✗ {name} (HTTP {resp.status})"
        except Exception as e:
            return f"✗ {name} ({str(e)})"
        finally:
            conn.close()
    
    def delete_asset(self, asset_info, tracker):
        """删除单个壁纸文件"""
        name, _, dest_path = asset_info
        try:
            if os.path.exists(dest_path):
                file_size = os.path.getsize(dest_path)
                os.remove(dest_path)
                with self.lock:
                    tracker.update(file_size)
                return f"✓ 已删除 {name}"
            return f"✗ 文件不存在 {name}"
        except Exception as e:
            return f"✗ 删除失败 {name} ({str(e)})"

class ProgressTracker:
    """进度跟踪器"""
    def __init__(self, total_files, total_size):
        self.start_time = time.time()
        self.total_files = total_files
        self.total_size = total_size
        self.completed_files = 0
        self.completed_size = 0
    
    def update(self, file_size):
        """更新进度"""
        self.completed_files += 1
        self.completed_size += file_size
    
    def get_progress(self):
        """获取当前进度"""
        elapsed = time.time() - self.start_time
        progress = self.completed_size / self.total_size if self.total_size > 0 else 0
        speed = self.completed_size / elapsed if elapsed > 0 else 0
        remaining = (self.total_size - self.completed_size) / speed if speed > 0 else 0
        
        return (
            progress,
            speed,
            self.format_time(elapsed),
            self.format_time(remaining)
        )
    
    @staticmethod
    def format_time(seconds):
        """格式化时间显示"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds//60)}分{int(seconds%60)}秒"
        else:
            return f"{int(seconds//3600)}时{int((seconds%3600)//60)}分"

def format_size(bytes):
    """格式化文件大小"""
    if bytes == 0:
        return "0B"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}TB"

def display_progress(tracker, total_files, action):
    """显示进度条"""
    while tracker.completed_files < total_files:
        progress, speed, elapsed, remaining = tracker.get_progress()
        
        # 进度条
        bar_width = 50
        completed_width = int(bar_width * progress)
        progress_bar = f"[{'=' * completed_width}{' ' * (bar_width - completed_width)}]"
        
        # 显示信息
        print(
            f"\r{action} {progress_bar} {progress*100:.1f}% | "
            f"{tracker.completed_files}/{total_files}文件 | "
            f"{format_size(tracker.completed_size)}/{format_size(tracker.total_size)} | "
            f"速度: {format_size(speed)}/s | 用时: {elapsed} | 剩余: {remaining}",
            end="", flush=True
        )
        time.sleep(0.5)
    print()

def verify_environment():
    """验证系统环境"""
    required_paths = [
        IDLEASSETSD_PATH,
        STRINGS_PATH,
        ENTRIES_PATH,
        VIDEO_PATH
    ]
    for path in required_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"系统路径不存在: {path}")

def main():
    print("macOS 动态壁纸管理器")
    print("-------------------\n")
    
    # 检查权限
    if os.geteuid() != 0:
        print("请使用sudo运行此脚本:")
        print(f"  sudo python3 {os.path.basename(__file__)}")
        exit(1)
    
    # 验证环境
    try:
        verify_environment()
    except FileNotFoundError as e:
        print(f"错误: {str(e)}")
        print("请确保: 1) 运行在macOS系统 2) 使用sudo运行")
        exit(1)
    
    # 初始化管理器
    manager = WallpaperManager()
    manager.load_data()
    
    # 显示分类菜单
    print("\n可用壁纸分类:")
    for i, category in enumerate(manager.categories, 1):
        print(f"{i}. {manager.get_category_name(category)}")
    print(f"{len(manager.categories)+1}. 所有壁纸")
    
    # 选择分类
    try:
        choice = int(input("\n请选择分类编号: ")) - 1
        if choice < 0 or choice >= len(manager.categories)+1:
            print("无效选择!")
            exit(1)
        
        category_id = manager.categories[choice]["id"] if choice < len(manager.categories) else None
    except ValueError:
        print("请输入有效数字!")
        exit(1)
    
    # 选择操作
    action = input("\n请选择操作: (d)下载 (x)删除 (q)退出: ").lower()
    if action not in ['d', 'x']:
        exit()
    
    action_text = "下载" if action == 'd' else "删除"
    
    # 获取目标壁纸列表
    assets = manager.get_assets_by_category(category_id)
    if not assets:
        print("\n没有找到可操作的壁纸!")
        exit()
    
    # 计算总大小
    total_size = 0
    valid_assets = []
    
    print("\n正在计算大小...")
    for asset in assets:
        name, url, path = asset
        if action == 'd':
            if not os.path.exists(path):
                file_size = manager.get_file_size(url)
                total_size += file_size
                valid_assets.append(asset)
                print(f"  * 将{action_text}: {name} ({format_size(file_size)})")
            else:
                print(f"  - 已存在: {name}")
        else:
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                total_size += file_size
                valid_assets.append(asset)
                print(f"  * 将{action_text}: {name} ({format_size(file_size)})")
            else:
                print(f"  - 不存在: {name}")
    
    if not valid_assets:
        print("\n没有可操作的壁纸!")
        exit()
    
    # 检查磁盘空间(仅下载时)
    if action == 'd':
        free_space = shutil.disk_usage("/").free
        print(f"\n可用空间: {format_size(free_space)}")
        print(f"总{action_text}大小: {format_size(total_size)}")
        
        if total_size > free_space:
            print("错误: 磁盘空间不足!")
            exit(1)
    
    # 确认操作
    confirm = input(f"\n确认{action_text} {len(valid_assets)} 个壁纸? (y/n): ").lower()
    if confirm != 'y':
        exit()
    
    # 执行操作
    tracker = ProgressTracker(len(valid_assets), total_size)
    
    # 启动进度显示线程
    from threading import Thread
    progress_thread = Thread(
        target=display_progress,
        args=(tracker, len(valid_assets), action_text),
        daemon=True
    )
    progress_thread.start()
    
    # 使用线程池执行操作
    results = []
    with ThreadPool(8) as pool:
        if action == 'd':
            results = pool.starmap(manager.download_asset, [(a, tracker) for a in valid_assets])
        else:
            results = pool.starmap(manager.delete_asset, [(a, tracker) for a in valid_assets])
    
    progress_thread.join()
    
    # 显示结果
    print(f"\n{action_text}完成!")
    print(f"总耗时: {tracker.format_time(time.time() - tracker.start_time)}")
    
    # 可选: 重启idleassetsd
    restart = input("\n重启idleassetsd服务以立即生效? (y/n): ").lower()
    if restart == 'y':
        os.system("killall idleassetsd")
        print("服务已重启")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
