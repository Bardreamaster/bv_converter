import json
import subprocess
import shutil
from pathlib import Path
import sharklog

_logger = sharklog.getLogger("bv_converter")


def sanitize_filename(name):
    """处理非法字符，确保文件名在 Windows/Linux/macOS 下安全"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()


def process_bili_cache(cache_root, export_dir):
    cache_path = Path(cache_root)
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)

    success_names = set()  # 用于记录已成功导出的文件名，避免重复
    fail_names = set()     # 用于记录处理失败的文件夹名

    # 递归查找包含 .m4s 的文件夹
    for subdir in cache_path.rglob('*'):
        if not subdir.is_dir():
            continue

        m4s_files = list(subdir.glob('*.m4s'))
        info_file = subdir / 'videoInfo.json'

        # 只有同时存在至少两个 m4s 和一个 info 文件才处理
        if len(m4s_files) >= 2 and info_file.exists():
            _logger.info(f"正在处理目录: {subdir.name}")
            temp_video = subdir / "v_temp.m4s"
            temp_audio = subdir / "a_temp.m4s"

            try:
                # 1. 解析标题和 BVID
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)

                # 兼容不同版本的 json 字段名（某些版本是 'title'，某些在 'data' 目录下）
                bvid = info.get('bvid', 'unknown_bvid')
                title = info.get('title') or info.get('data', {}).get('title', 'unknown_title')

                clean_title = sanitize_filename(f"{bvid}-{title}")
                output_file = export_path / f"{clean_title}.mp4"

                # 2. 区分音视频 (大的通常是视频)
                m4s_files.sort(key=lambda x: x.stat().st_size, reverse=True)
                video_raw = m4s_files[0]
                audio_raw = m4s_files[1]

                # 3. 去除文件头 (跳过前9个字节) 并保存到临时文件
                for raw, temp in [(video_raw, temp_video), (audio_raw, temp_audio)]:
                    with open(raw, 'rb') as f_in:
                        f_in.seek(9)  # 跳过 Bilibili 自定义的 9 字节头
                        with open(temp, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                # 4. 调用 FFmpeg 合并
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', str(temp_video),
                    '-i', str(temp_audio),
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    str(output_file),
                    '-loglevel', 'error'
                ]

                subprocess.run(ffmpeg_cmd, check=True)
                _logger.info(f"成功导出: {output_file.name}")
                success_names.add(output_file.name)

            except Exception as e:
                _logger.error(f"处理 {subdir.name} 时出错: {e}")
                fail_names.add(subdir.name)

            finally:
                # 5. 清理临时文件
                if temp_video.exists():
                    temp_video.unlink()
                if temp_audio.exists():
                    temp_audio.unlink()

    # 输出处理结果
    _logger.info(f"处理完成！成功导出 {len(success_names)} 个文件, 失败 {len(fail_names)} 个文件。")
    if success_names:
        _logger.info("成功导出的文件:")
        for name in success_names:
            _logger.info(f"  - {name}")
    if fail_names:
        _logger.info("处理失败的目录:")
        for name in fail_names:
            _logger.info(f"  - {name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='将B站缓存中的.m4s文件转换为.mp4格式'
    )
    parser.add_argument('cache_dir', help='B站缓存根目录路径')
    parser.add_argument('export_dir', help='导出目录路径')

    args = parser.parse_args()

    sharklog.init()
    process_bili_cache(args.cache_dir, args.export_dir)


if __name__ == "__main__":
    main()
