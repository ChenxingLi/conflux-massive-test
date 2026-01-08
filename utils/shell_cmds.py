import subprocess
import time
from typing import List

from loguru import logger

def scp(script_path: str, ip_address: str, user: str = "ubuntu", remote_path: str = "~"):
    scp_cmd = [
        'scp',
        '-o', 'StrictHostKeyChecking=no',
        "-o", "UserKnownHostsFile=/dev/null",
        script_path,
        f'{user}@{ip_address}:{remote_path}'
    ]
    subprocess.run(scp_cmd, check=True, capture_output=True)

def rsync_download(remote_path: str, local_path: str, ip_address: str, *, user: str = "ubuntu", compress_level: int = 12, max_retries: int = 3):
    rsync_cmd = [
        'rsync',
        '-az',  # -a: archive mode, -v: verbose, -z: compress
        # '--whole-file',  # 跳过差异对比，直接传输整个文件
        '--compress-choice=zstd',  # 使用 zstd 压缩
        f'--compress-level={compress_level}',  # 压缩级别 12
        '-e', 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null',  # SSH 选项
        f'{user}@{ip_address}:{remote_path}',
        local_path,
    ]
    # Python 层面实现重试
    for attempt in range(max_retries):
        try:
            subprocess.run(rsync_cmd, check=True, capture_output=True)
            return  # 成功则返回
        except subprocess.CalledProcessError as e:
            if attempt == max_retries - 1:  # 最后一次尝试
                logger.warning(f"Cannot download files from {user}@{ip_address}:{remote_path} to {local_path}: {e}")
                raise Exception("Cannot download")
            # print(f"Attempt {attempt + 1} failed, retrying...")
        except subprocess.TimeoutExpired as e:
            if attempt == max_retries - 1:
                logger.warning(f"Cannot download files from {user}@{ip_address}:{remote_path} to {local_path}: {e}")
                raise Exception("Cannot download")
            # print(f"Timeout on attempt {attempt + 1}, retrying...")

def ssh(ip_address: str, user: str = "ubuntu", command: str | List[str] | None = None, *, max_retries: int = 3, retry_delay: int = 15):
    if command is None:
        return
    
    if type(command) is str:
        command = [command]

    ssh_cmd = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        "-o", "UserKnownHostsFile=/dev/null",
        f'{user}@{ip_address}',
        *command
    ]

    for attempt in range(max_retries):
        try:
            result = subprocess.run(ssh_cmd, check=True, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                logger.debug(f"{ip_address} SSH 失败 (尝试 {attempt + 1}/{max_retries}), {retry_delay} 秒后重试...  {e}")
                time.sleep(retry_delay)
            else:
                logger.debug(f"{ip_address} SSH 失败，已达到最大重试次数")
                raise