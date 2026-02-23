# bv_converter

将B站缓存中的 `.m4s` 文件转换为 `.mp4` 格式，并导出到指定目录。

## 功能特性

- 自动递归搜索缓存目录中的所有视频
- 智能识别音频和视频流并合并
- 从 `videoInfo.json` 提取视频标题和 BVID

## 安装

### 前置依赖

确保已安装 [FFmpeg](https://ffmpeg.org/download.html)：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 使用 pip 安装

```bash
pip install bv-converter
```

### 从源码安装

```bash
git clone https://github.com/jinqi/bv_converter.git
cd bv_converter
python3 -m pip install -e .
```

## 使用方法

```bash
bv_converter <cache_dir> <export_dir>
```

### 参数说明

- `cache_dir`: B 站缓存根目录路径
- `export_dir`: 导出 MP4 文件的目标目录

### 示例

```bash
# macOS/Linux
bv_converter ~/Movies/bilibili ~/Movies/bilibili/output
```
