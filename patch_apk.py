#!/usr/bin/env python3
import os
import subprocess
import xml.etree.ElementTree as ET
import re
import shutil
import yaml

APK_TOOL = "apktool"
OUTPUT_DIR = "patched_apks"
APK_VERSION = None 
AAPT2 = "aapt2"
USE_AAPT2_OPTIMIZE = False   
KEYSTORE_PATH = "./origin-twitter.keystore"
ALIAS = "origin"
STOREPASS = "123456789"
KEYPASS = "123456789"

THEME_COLORS = {
    "1d9bf0": "Blue",
    "fed400": "Gold",
    "f91880": "Red",
    "7856ff": "Purple",
    "ff7a00": "Orange",
    "31c88e": "Green",
    "c20024": "Crimsonate",
    "1e50a2": "Lazurite",
    "808080": "Monotone",
    "ffadc0": "MateChan"
}

# Obtaining the version from GitHub environment variables
apk_version = os.getenv('CRIMERA_TAG')  
apk_file_name = f"twitter-piko-v{apk_version}.apk" 
apk_path = f"downloads/{apk_file_name}"  

print(f"APK Path: {apk_path}")

def decompile_apk(apk_path, output_path):
    print(f"Checking if APK file exists: {apk_path}")
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK file not found: {apk_path}")
    subprocess.run([APK_TOOL, "d", apk_path, "-o", output_path, "--force"], check=True)

def update_apktool_yml(decompiled_path):
    """
    Update apktool.yml so that .so files are not recompressed
    """
    yml_path = os.path.join(decompiled_path, "apktool.yml")
    if os.path.exists(yml_path):
        print(f"Updating doNotCompress in {yml_path}")
        with open(yml_path, "r", encoding="utf-8") as f:
            yml_data = yaml.safe_load(f)
        doNotCompress = yml_data.get("doNotCompress", [])
        if ".so" not in doNotCompress and "so" not in doNotCompress:
            doNotCompress.append(".so")
        yml_data["doNotCompress"] = doNotCompress
        with open(yml_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(yml_data, f)
    else:
        print(f"{yml_path} not found. Skipping update for doNotCompress.")

def modify_manifest(decompiled_path):
    """
    Change the android:extractNativeLibs attribute of the <application> tag in AndroidManifest.xml to true
    """
    manifest_path = os.path.join(decompiled_path, "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        return
    ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    application = root.find('application')
    if application is not None:
        application.set("{http://schemas.android.com/apk/res/android}extractNativeLibs", "true")
        tree.write(manifest_path, encoding="utf-8", xml_declaration=True)
        print("Modified AndroidManifest.xml: set android:extractNativeLibs to true")

def get_apk_version(apk_path):
    global APK_VERSION
    match = re.search(r"twitter-piko-v(\d+\.\d+\.\d+)", apk_path)
    if match:
        APK_VERSION = match.group(1)
    else:
        APK_VERSION = "unknown"
    print(f"Detected APK Version: {APK_VERSION}")

def modify_xml(decompiled_path):
    xml_files = [
        "res/layout/ocf_twitter_logo.xml",
        "res/layout/login_toolbar_seamful_custom_view.xml"
    ]
    for xml_file in xml_files:
        file_path = os.path.join(decompiled_path, xml_file)
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("?dynamicColorGray1100", "@color/twitter_blue")
        content = content.replace("@color/gray_1100", "@color/twitter_blue")
        content = re.sub(r"#ff1d9bf0|#ff1da1f2", "@color/twitter_blue", content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def modify_styles(decompiled_path):
    styles_path = os.path.join(decompiled_path, "res/values/styles.xml")
    if not os.path.exists(styles_path):
        return
    tree = ET.parse(styles_path)
    root = tree.getroot()
    for style in root.findall("style"):
        name = style.get("name", "")
        if name in ["TwitterBase.Dim", "TwitterBase.LightsOut", "TwitterBase.Standard"]:
            for item in style.findall("item"):
                if item.get("name") == "coreColorBadgeVerified":
                    item.text = "@color/blue_500"
        elif name in ["PaletteDim", "PaletteLightsOut", "PaletteStandard"]:
            for item in style.findall("item"):
                if item.get("name") == "abstractColorUnread":
                    item.text = "@color/twitter_blue_opacity_50"
                elif item.get("name") == "abstractColorLink" and name == "PaletteStandard":
                    item.text = "@color/twitter_blue"
        elif name in ["Theme.LaunchScreen"]:
            for item in style.findall("item"):
                if item.get("name") == "windowSplashScreenBackground":
                    item.text = "@color/twitter_blue"
    tree.write(styles_path, encoding="utf-8", xml_declaration=True)

def modify_colors(decompiled_path, color):
    colors_path = os.path.join(decompiled_path, "res/values/colors.xml")
    if not os.path.exists(colors_path):
        return
    tree = ET.parse(colors_path)
    root = tree.getroot()
    hex_color = f"#ff{color}"
    opacity_map = {
        "twitter_blue": hex_color,
        "deep_transparent_twitter_blue": f"#cc{color}",
        "twitter_blue_opacity_30": f"#4d{color}",
        "twitter_blue_opacity_50": f"#80{color}",
        "twitter_blue_opacity_58": f"#95{color}"
    }
    for color_tag in root.findall("color"):
        name = color_tag.get("name", "")
        if name in opacity_map:
            color_tag.text = opacity_map[name]
    tree.write(colors_path, encoding="utf-8", xml_declaration=True)

def hex_to_smali(hex_color):
    int_color = int(hex_color, 16)
    smali_int = (int_color ^ 0xFFFFFF) + 1
    smali_value = f"-0x{smali_int:06x}"
    return smali_value.lower()

def modify_smali(decompiled_path, color):
    smali_color = hex_to_smali(color) + "00000000L"
    patterns = {
        re.compile(r"-0xe2641000000000L", re.IGNORECASE): smali_color, 
        re.compile(r"0xff1d9bf0L", re.IGNORECASE): f"0xff{color}L",  
    }
    print(f"Scanning all .smali files under: {decompiled_path}")
    for root_dir, _, files in os.walk(decompiled_path):
        for file in files:
            if file.endswith(".smali"):
                smali_path = os.path.join(root_dir, file)
                with open(smali_path, "r", encoding="utf-8") as f:
                    content = f.read()
                original_content = content
                for pattern, replacement in patterns.items():
                    content = pattern.sub(replacement, content)
                if content != original_content:
                    with open(smali_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Modified: {smali_path}")

def get_zipalign_path():
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not android_home:
        raise FileNotFoundError("ANDROID_HOME or ANDROID_SDK_ROOT is not set.")
    build_tools_dir = os.path.join(android_home, "build-tools")
    versions = sorted(os.listdir(build_tools_dir), reverse=True)
    for version in versions:
        zipalign_path = os.path.join(build_tools_dir, version, "zipalign")
        if os.path.exists(zipalign_path):
            return zipalign_path
    raise FileNotFoundError("zipalign was not found.")

def get_apksigner_path():
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not android_home:
        raise FileNotFoundError("ANDROID_HOME or ANDROID_SDK_ROOT is not set.")
    build_tools_dir = os.path.join(android_home, "build-tools")
    versions = sorted(os.listdir(build_tools_dir), reverse=True)
    for version in versions:
        apksigner_path = os.path.join(build_tools_dir, version, "apksigner")
        if os.path.exists(apksigner_path):
            return apksigner_path
    raise FileNotFoundError("apksigner was not found")

def recompile_apk(decompiled_path, output_apk):
    subprocess.run([APK_TOOL, "b", decompiled_path, "-o", output_apk], check=True)

def optimize_resources_arsc(apk_path):
    optimized_apk = apk_path + ".optimized"
    subprocess.run([
        AAPT2, "optimize",
        "--shorten-resource-paths",
        "--enable-sparse-encoding",
        "--deduplicate-entry-values",
        apk_path,
        "-o", optimized_apk
    ], check=True)
    shutil.move(optimized_apk, apk_path)
    print(f"✅ Optimized resources.arsc: {apk_path}")

def align_resources_arsc(apk_path):
    zipalign_path = get_zipalign_path()
    aligned_apk = apk_path + ".aligned"
    subprocess.run([zipalign_path, "-v", "4", apk_path, aligned_apk], check=True)
    shutil.move(aligned_apk, apk_path)
    print(f"✅ resources.arsc is now placed on a 4-byte boundary: {apk_path}")

def sign_apk(apk_path):
    zipalign_path = get_zipalign_path()
    apksigner_path = get_apksigner_path()
    if USE_AAPT2_OPTIMIZE:
        optimize_resources_arsc(apk_path)
    align_resources_arsc(apk_path)
    subprocess.run([
        apksigner_path,
        "sign",
        "--ks", KEYSTORE_PATH,
        "--ks-pass", f"pass:{STOREPASS}",
        "--ks-key-alias", ALIAS,
        "--key-pass", f"pass:{KEYPASS}",
        "--v1-signing-enabled", "true",
        "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true",
        "--v4-signing-enabled", "false",
        apk_path
    ], check=True)
    subprocess.run([apksigner_path, "verify", "--print-certs", apk_path], check=True)
    return apk_path

def patch_apk(apk_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    get_apk_version(apk_path)
    for color, name in THEME_COLORS.items():
        decompiled_path = f"{apk_path}_decompiled_{color}"
        patched_apk = os.path.join(OUTPUT_DIR, f"Origin-Twitter.{name}.v{APK_VERSION}-release.0.apk")
        print(f"\nProcessing theme color {color} ({name})")
        decompile_apk(apk_path, decompiled_path)
        update_apktool_yml(decompiled_path)  
        modify_manifest(decompiled_path)     
        modify_xml(decompiled_path)
        modify_styles(decompiled_path)
        modify_colors(decompiled_path, color)
        modify_smali(decompiled_path, color)
        recompile_apk(decompiled_path, patched_apk)
        sign_apk(patched_apk)
        print(f"Generated: {patched_apk}")

if __name__ == "__main__":
    print(f"Detected APK Version: {apk_version}")
    patch_apk(apk_path)
