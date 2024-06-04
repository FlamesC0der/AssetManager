import requests
from tqdm import tqdm
import os
import sys
import json
import threading

ROOT_DIR = os.path.dirname(__file__)

pbar_width = os.get_terminal_size().columns - 10


def check_asset(asset_path: str, asset_url: str):
    asset_name = asset_path.split("/")[-1]
    if os.path.isfile(os.path.join(ROOT_DIR, "assets", asset_name)):
        return True
    else:
        download_asset(asset_url, asset_path)


def download_asset(asset_link: str, asset_path: str):
    try:
        if not os.path.isdir(asset_path):
            try:
                os.makedirs(os.path.dirname(asset_path))
            except Exception:
                pass
        with requests.get(asset_link, stream=True) as r:
            r.raise_for_status()
            with open(asset_path, 'wb') as f:
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
    except KeyboardInterrupt:
        sys.exit("Asset download canceled by user")
    except Exception as e:
        print(f"An error occurred while downloading asset: {e}")
        sys.exit(f"An error occurred while downloading asset")


def check_all_assets():
    with open(os.path.join(ROOT_DIR, "assets.json")) as f:
        assets = json.load(f)

    download_tasks = {}

    for i, asset in enumerate(assets.keys()):
        download_tasks[i] = threading.Thread(target=check_asset, args=(asset, assets[asset]))
    for i in download_tasks:
        download_tasks[i].start()
    for i in download_tasks:
        download_tasks[i].join()
