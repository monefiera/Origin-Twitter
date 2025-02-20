import os
import re
import requests


GITHUB_REPO = "monefiera/Origin-Twitter" 
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
APK_DIR = "patched_apks"
DOWNLOAD_DIR = "downloads"

# 1. Get version and release ID from downloaded APK
def extract_version_and_release_id():
    for apk_name in os.listdir(DOWNLOAD_DIR):
        match = re.search(r"twitter-piko-v?(\d+\.\d+\.\d+)-release\.(\d+)\.apk", apk_name)
        if match:
            version, release_id = match.groups()
            print(f"Detected APK Version: {version}, Release ID: {release_id}")
            return version, release_id
    print("Error: Unable to extract version and release ID.")
    return None, None

# 2. Create a new release on GitHub
def create_github_release(version, release_id):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "tag_name": f"{version}-release.{release_id}",
        "name": f"Origin Twitter v{version}-release.{release_id}",
        "body": f"Auto-generated release: Origin Twitter version {version}-release.{release_id}.",
        "draft": False,
        "prerelease": False
    }
    response = requests.post(GITHUB_API, json=data, headers=headers)
    if response.status_code == 201:
        release_info = response.json()
        print(f"GitHub Release created: {release_info['html_url']}")
        return release_info["id"], release_info["upload_url"].split("{")[0]
    else:
        print(f"Failed to create release: {response.text}")
        return None, None

# 3. Upload APK
def upload_apk_to_github(release_id, upload_url, apk_path):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/vnd.android.package-archive"
    }
    file_name = os.path.basename(apk_path)
    with open(apk_path, "rb") as apk_file:
        response = requests.post(f"{upload_url}?name={file_name}", headers=headers, data=apk_file)
    
    if response.status_code == 201:
        print(f"Successfully uploaded {file_name}")
    else:
        print(f"Failed to upload {file_name}: {response.text}")

# 4. Execution of all processes
def release_apks():
    version, release_id = extract_version_and_release_id()
    if not version or not release_id:
        return
    github_release_id, upload_url = create_github_release(version, release_id)
    if not github_release_id:
        return
    for apk_file in os.listdir(APK_DIR):
        if apk_file.endswith(".apk"):
            apk_path = os.path.join(APK_DIR, apk_file)
            upload_apk_to_github(github_release_id, upload_url, apk_path)

if __name__ == "__main__":
    release_apks()
