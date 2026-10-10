import os
import re
import requests

GITHUB_REPO = "monefiera/Origin-Twitter"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases"

APK_DIR = "patched_apks"
DOWNLOAD_DIR = "downloads"


def github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def extract_version_and_release_id():
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"Error: '{DOWNLOAD_DIR}' does not exist.")
        return None, None
    for apk_name in os.listdir(DOWNLOAD_DIR):
        match = re.search(
            r"twitter-piko-v?(\d+\.\d+\.\d+)-release\.(\d+)\.apk",
            apk_name
        )
        if match:
            version, release_id = match.groups()
            print(
                f"Detected APK Version: {version}, "
                f"Release ID: {release_id}"
            )
            return version, release_id
    print("Error: Unable to extract version and release ID.")
    return None, None

def find_release_by_tag(tag_name):
    response = requests.get(
        GITHUB_API,
        headers=github_headers()
    )
    if response.status_code != 200:
        print("Failed to fetch releases.")
        print(response.text)
        return None
    for release in response.json():
        if release["tag_name"] == tag_name:
            return release
    return None

def get_or_create_prerelease(version, release_number):
    tag_name = f"{version}-pre-release.{release_number}"
    release = find_release_by_tag(tag_name)

    if release:
        print(f"Using existing release: {tag_name}")

        return (
            release["id"],
            release["upload_url"].split("{")[0]
        )
    print(f"Creating release: {tag_name}")
    payload = {
        "tag_name": tag_name,
        "name": (
            f"Origin Twitter "
            f"v{version}-release.{release_number} "
            f"(Pre-release)"
        ),
        "body": (
            f"Auto-generated pre-release:\n\n"
            f"Version: {version}\n"
            f"Release: {release_number}"
        ),
        "draft": False,
        "prerelease": True
    }
    response = requests.post(
        GITHUB_API,
        json=payload,
        headers=github_headers()
    )
    if response.status_code == 201:
        release = response.json()
        print(
            f"Created release: "
            f"{release['html_url']}"
        )
        return (
            release["id"],
            release["upload_url"].split("{")[0]
        )
    print("Failed to create release.")
    print(response.text)
    return None, None

def get_release_assets(release_id):
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/releases/{release_id}/assets"
    )
    response = requests.get(
        url,
        headers=github_headers()
    )
    if response.status_code != 200:
        print("Failed to fetch assets.")
        return []
    return response.json()


def delete_existing_asset(release_id, asset_name):
    assets = get_release_assets(release_id)
    for asset in assets:
        if asset["name"] != asset_name:
            continue
        asset_id = asset["id"]
        delete_url = (
            f"https://api.github.com/repos/"
            f"{GITHUB_REPO}/releases/assets/{asset_id}"
        )

        print(f"Deleting existing asset: {asset_name}")
        response = requests.delete(
            delete_url,
            headers=github_headers()
        )
        if response.status_code == 204:
            print(f"Deleted: {asset_name}")
        else:
            print(
                f"Failed to delete asset: "
                f"{response.text}"
            )


def upload_apk_to_github(
    release_id,
    upload_url,
    apk_path
):
    file_name = os.path.basename(apk_path)
    delete_existing_asset(
        release_id,
        file_name
    )
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type":
            "application/vnd.android.package-archive"
    }
    upload_endpoint = (
        f"{upload_url}?name={file_name}"
    )
    print(f"Uploading: {file_name}")
    with open(apk_path, "rb") as apk_file:

        response = requests.post(
            upload_endpoint,
            headers=headers,
            data=apk_file
        )
    if response.status_code == 201:
        print(
            f"Successfully uploaded: "
            f"{file_name}"
        )
    else:
        print(
            f"Failed to upload: "
            f"{file_name}"
        )
        print(response.text)

def release_apks():

    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN is not set.")
        return
    version, release_number = (
        extract_version_and_release_id()
    )
    if not version or not release_number:
        return
    release_id, upload_url = (
        get_or_create_prerelease(
            version,
            release_number
        )
    )
    if not release_id:
        return
    if not os.path.exists(APK_DIR):
        print(
            f"Error: '{APK_DIR}' does not exist."
        )
        return

    apk_files = [
        f for f in os.listdir(APK_DIR)
        if f.endswith(".apk")
    ]
    if not apk_files:
        print("No APK files found.")
        return
    for apk_file in apk_files:
        apk_path = os.path.join(
            APK_DIR,
            apk_file
        )
        upload_apk_to_github(
            release_id,
            upload_url,
            apk_path
        )
    print("Release process completed.")


if __name__ == "__main__":
    release_apks()
