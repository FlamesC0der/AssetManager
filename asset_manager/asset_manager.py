import requests
from tqdm import tqdm
import os
import sys
import json
import threading
from pathlib import Path

from misc import ROOT_DIR

try:
    pbar_width = os.get_terminal_size().columns - 10
except Exception:
    pbar_width = 100


def check_asset(asset_path: str, asset_url: str, index: int, status: bool, task_statuses: dict):
    asset_full_path = os.path.join(ROOT_DIR, "assets", asset_path)
    asset_path = '/'.join(asset_full_path.split("/")[:-1])
    asset_name = asset_path.split("/")[-1]
    if not os.path.isfile(asset_full_path):
        download_asset(asset_full_path, asset_path, asset_name, asset_url)
    task_statuses[index] = (asset_path, asset_url, index, True, task_statuses)


def download_asset(asset_full_path: str, asset_path: str, asset_name: str, asset_link: str):
    try:
        Path(asset_path).mkdir(parents=True, exist_ok=True)
        with requests.get(asset_link, stream=True) as r:
            r.raise_for_status()
            with open(asset_full_path, 'wb') as f:
                pbar = tqdm(
                    total=int(r.headers['Content-Length']),
                    unit="B",
                    unit_scale=True,
                    ncols=pbar_width,
                    colour="WHITE",
                    leave=False
                )
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    except Exception as e:
        sys.exit()


def check_all_assets():
    with open(os.path.join(ROOT_DIR, "asset_manager", "assets.json")) as f:
        assets = json.load(f)

    download_tasks = {}
    task_statuses = {}

    for i, asset in enumerate(assets.keys()):
        task_statuses[i] = (asset, assets[asset], i, False, task_statuses)

    try:
        for i, asset in enumerate(assets.keys()):
            download_tasks[i] = threading.Thread(target=check_asset, args=task_statuses[i])
        for i in download_tasks:
            download_tasks[i].start()
        for i in download_tasks:
            download_tasks[i].join()
    except KeyboardInterrupt:  # Remove cancelled downloads
        for task in task_statuses.keys():
            if not task_statuses[task][3]:
                os.remove(os.path.join(ROOT_DIR, "assets", task_statuses[task][0]))
        sys.exit()
