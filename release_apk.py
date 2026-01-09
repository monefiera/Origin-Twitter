#!/usr/bin/env python3

import os
import re
import requests
import sys
import glob

GITHUB_REPO = "monefiera/Origin-Twitter"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable is not set.")
    sys.exit(1)

GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
APK_DIR = "patched_apks"

def extract_version_from_downloaded_apk():
    """ダウンロードしたAPKのファイル名から正確なバージョンを抽出"""
    print("Looking for downloaded APK file...")
    
    # 修正点: 単純な置換ではなく、正規表現で正確にバージョンを抽出
    monsivamon_tag = os.getenv('monsivamon_TAG')
    if not monsivamon_tag:
        print("Error: monsivamon_TAG is not set.")
        return None, None
    
    print(f"Raw monsivamon_TAG from env: {monsivamon_tag}")
    
    # 例: "11.46.0-release.0" から "11.46.0" と "0" を抽出
    version_pattern = r'(\d+\.\d+\.\d+)-release\.(\d+)'
    match = re.match(version_pattern, monsivamon_tag)
    
    if match:
        version = match.group(1)  # "11.46.0"
        release_id = match.group(2)  # "0"
        print(f"✅ Parsed version: {version}, release_id: {release_id}")
        return version, release_id
    else:
        # フォールバック: 環境変数から直接抽出を試みる
        clean_version = monsivamon_tag.split('-release')[0]
        version = clean_version
        release_id = "0"
        print(f"⚠️  Using fallback version: {version}, release_id: {release_id}")
        return version, release_id

def create_github_release(version, release_id):
    """GitHubリリースを作成"""
    # 修正点: 正しいフォーマットのタグ名を作成
    tag_name = f"{version}-release.{release_id}"
    print(f"Creating GitHub release with tag: {tag_name}")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. 既存のリリースをチェック
    response = requests.get(GITHUB_API, headers=headers)
    if response.status_code == 200:
        releases = response.json()
        for release in releases:
            if release.get("tag_name") == tag_name:
                print(f"✅ Release {tag_name} already exists. Using existing release.")
                return release["id"], release["upload_url"].split("{")[0]
    
    # 2. 新規リリース作成
    # 修正点: 詳細なリリース本文を使用
    body = f"""自動リリース: Origin Twitter Neo version {version}-release.{release_id}

## Available Color Themes
- Blue
- Gold
- Red
- Purple
- Orange
- Green
- Crimsonate
- Lazurite
- Monotone
- MateChan

## Notes
- All color variants use the same signature for easy switching
- Based on monsivamon's Piko Twitter mod
"""
    
    data = {
        "tag_name": tag_name,
        "name": f"Origin Twitter v{version}-release.{release_id}",
        "body": body,  # 修正: 詳細なbody変数を使用
        "draft": False,
        "prerelease": False
    }
    
    response = requests.post(GITHUB_API, json=data, headers=headers)
    print(f"Create release response status: {response.status_code}")
    
    if response.status_code == 201:
        release_info = response.json()
        print(f"✅ GitHub Release created: {release_info['html_url']}")
        return release_info["id"], release_info["upload_url"].split("{")[0]
    else:
        print(f"❌ Failed to create release: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None

def upload_apk_to_github(release_id, upload_url, apk_path):
    print(f"Uploading APK: {apk_path}")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/vnd.android.package-archive",
        "Accept": "application/vnd.github.v3+json"
    }
    
    file_name = os.path.basename(apk_path)
    
    # 既存のアセットをチェックして削除
    assets_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/{release_id}/assets"
    response = requests.get(assets_url, headers=headers)
    
    if response.status_code == 200:
        assets = response.json()
        for asset in assets:
            if asset["name"] == file_name:
                print(f"Asset {file_name} already exists. Deleting...")
                delete_response = requests.delete(asset["url"], headers=headers)
                if delete_response.status_code == 204:
                    print(f"Deleted existing asset: {file_name}")
    
    # 新しいAPKをアップロード
    with open(apk_path, "rb") as apk_file:
        response = requests.post(f"{upload_url}?name={file_name}", headers=headers, data=apk_file)
    
    if response.status_code == 201:
        print(f"✅ Successfully uploaded {file_name}")
        return True
    elif response.status_code == 422:
        # 422エラーはアセットが既に存在する場合が多い
        print(f"⚠️  Asset may already exist (422): {file_name}")
        return True
    else:
        print(f"❌ Failed to upload {file_name}: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def release_apks():
    print("Starting APK release process...")
    
    # 修正: 正しい関数名を呼び出す
    version, release_id = extract_version_from_downloaded_apk()
    if not version or not release_id:
        print("Could not extract version information.")
        return
    
    print(f"Using version: {version}, release_id: {release_id}")
    
    # GitHubリリースを作成
    github_release_id, upload_url = create_github_release(version, release_id)
    if not github_release_id:
        print("Failed to create GitHub release.")
        return
    
    # patched_apksディレクトリからAPKをアップロード
    if not os.path.exists(APK_DIR):
        print(f"Directory {APK_DIR} does not exist.")
        return
    
    apk_files = list(glob.glob(os.path.join(APK_DIR, "*.apk")))
    if not apk_files:
        print(f"No APK files found in {APK_DIR}")
        return
    
    print(f"Found {len(apk_files)} APK file(s):")
    for apk_file in sorted(apk_files):
        print(f"  - {os.path.basename(apk_file)}")
    
    # 各APKをアップロード
    success_count = 0
    for apk_file in sorted(apk_files):
        apk_name = os.path.basename(apk_file)
        print(f"\nProcessing {apk_name}...")
        
        if upload_apk_to_github(github_release_id, upload_url, apk_file):
            success_count += 1
    
    print(f"\n✅ Release process completed.")
    print(f"Successfully uploaded {success_count}/{len(apk_files)} files.")

if __name__ == "__main__":
    release_apks()
