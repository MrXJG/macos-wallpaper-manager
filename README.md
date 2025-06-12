根据你提供的 `wallpaper_manager.py` 脚本，我重新编写了准确反映其功能的 README.md 文件，包含必要的符号和简洁说明：

```markdown
# 🖼 macOS 动态壁纸管理器

> 一键批量下载/删除 macOS 官方动态壁纸 (4K SDR 240FPS)

## 🚀 核心功能
- ✅ 按分类批量下载 Apple 官方动态壁纸
- 🗑️ 批量删除已下载壁纸
- 📊 实时下载进度显示（速度/大小/剩余时间）
- 🔍 自动检测磁盘空间
- 🔄 支持重启 `idleassetsd` 服务立即生效

## ⚙️ 使用前提
1. **系统要求**  
   - macOS 10.14+
   - Python 3.9+

2. **权限要求**  
   ```bash
   # 必须使用 sudo 运行
   sudo python3 wallpaper_manager.py
   ```

## 🛠 使用步骤

### 1. 下载脚本
```bash
curl -O https://raw.githubusercontent.com/xiangjigong/macos-wallpaper-manager/main/wallpaper_manager.py
```

### 2. 运行程序
```bash
sudo python3 wallpaper_manager.py
```

### 3. 选择壁纸分类
```
macOS 动态壁纸管理器
-------------------

可用壁纸分类:
1. 自然
2. 城市
3. 水下
4. 所有壁纸
请选择分类编号: 
```

### 4. 选择操作
```
请选择操作: (d)下载 (x)删除 (q)退出: d
```

### 5. 确认操作
```
正在计算大小...
  * 将下载: 加州海岸 (45.2MB)
  * 将下载: 夏威夷海浪 (52.1MB)

可用空间: 128.4GB
总下载大小: 97.3MB

确认下载 2 个壁纸? (y/n): y
```

### 6. 查看进度
```
下载 [==================================================] 100.0% | 2/2文件 | 97.3MB/97.3MB | 速度: 8.4MB/s | 用时: 11秒 | 剩余: 0秒
```

### 7. 重启服务（可选）
```
重启idleassetsd服务以立即生效? (y/n): y
服务已重启
```

## ⚠️ 重要注意事项
1. **必须使用管理员权限运行**
   ```bash
   sudo python3 wallpaper_manager.py
   ```

2. **系统文件访问**
   - 脚本需要访问系统路径：
     ```
     /Library/Application Support/com.apple.idleassetsd
     ```

3. **磁盘空间检查**
   - 下载前会自动检测可用空间
   - 每个壁纸约 15-50MB

4. **网络要求**
   - 需能访问 Apple 壁纸服务器
   - 部分地区可能需要代理

## ❓ 常见问题
**Q：运行时提示 "系统路径不存在"**  
A：请确认：
1. 使用最新版 macOS
2. 已启用动态壁纸功能
3. 使用 `sudo` 运行

**Q：下载速度慢/失败**  
A：尝试：
1. 检查网络连接
2. 重启程序重试
3. 使用网络代理

**Q：如何查看下载的壁纸文件？**  
壁纸保存位置：
```
/Library/Application Support/com.apple.idleassetsd/Customer/4KSDR240FPS/
```

---

📄 [查看开源许可证](LICENSE) | 📧 反馈问题: xiangjigong@qq.com
```
