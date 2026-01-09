#!/usr/bin/env python3

import os
import subprocess
import yaml
import xml.etree.ElementTree as ET
import re
import sys
import shutil
import glob

# 環境変数から設定を読み込む（GitHub Actionsで設定したSecretsがここに入る）
KEYSTORE_PATH = "./origin-twitter.keystore"
ALIAS = os.environ.get("ALIAS", "origin")
STOREPASS = os.environ.get("STOREPASS", "123456789")  # デフォルト値はローカルテスト用
KEYPASS = os.environ.get("KEYPASS", "123456789")

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

def get_apktool_path():
    """apktoolの実行パスを取得する"""
    possible_paths = [
        '/usr/local/bin/apktool',
        ['java', '-jar', '/usr/local/bin/apktool.jar'],
        'apktool'
    ]
    
    for path_spec in possible_paths:
        cmd = []
        if isinstance(path_spec, list):
            cmd = path_spec + ['--version']
        else:
            cmd = [path_spec, '--version']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
            if result.returncode == 0:
                print(f"✅ apktool found: {' '.join(cmd)}")
                return path_spec
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("❌ Error: Could not find a working apktool path")
    return None

print("=== Initializing patch_apk.py ===")
APK_TOOL = get_apktool_path()
if APK_TOOL is None:
    print("FATAL: apktool is not available.")
    sys.exit(1)

def main():
    monsivamon_tag = os.getenv('monsivamon_TAG')
    if not monsivamon_tag or monsivamon_tag.lower() == 'null':
        print("Error: monsivamon_TAG is not set or null.")
        sys.exit(1)
    
    print(f"Original monsivamon_TAG: {monsivamon_tag}")
    
    # APKファイルのパスを特定
    apk_path = None
    downloads_dir = "downloads"
    
    if os.path.exists(downloads_dir):
        for filename in os.listdir(downloads_dir):
            if filename.endswith(".apk"):
                apk_path = os.path.join(downloads_dir, filename)
                break
    
    if not apk_path:
        print(f"Error: APK file not found in {downloads_dir}/")
        sys.exit(1)
    
    print(f"Found APK at: {apk_path}")
    
    # バージョン抽出
    version_pattern = r'(\d+\.\d+\.\d+)-release\.(\d+)'
    match = re.match(version_pattern, monsivamon_tag)
    if match:
        clean_version = match.group(1)
        release_id = match.group(2)
    else:
        clean_version = monsivamon_tag.split('-release')[0]
        release_id = "0"
    
    print(f"Clean version: {clean_version}, Release ID: {release_id}")
    
    OUTPUT_DIR = "patched_apks"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # キーストアの存在確認
    if not os.path.exists(KEYSTORE_PATH):
        print(f"❌ Error: Keystore file not found at {KEYSTORE_PATH}")
        print("Make sure you have set up the secrets and decoded the keystore properly.")
        sys.exit(1)
    
    for color_hex, color_name in THEME_COLORS.items():
        print(f"\n{'='*50}")
        print(f"Processing {color_name} theme (color: #{color_hex})")
        print(f"{'='*50}")
        
        decompiled_dir = f"decompiled-twitter-{clean_version}-{color_name}"
        
        try:
            decompile_apk(apk_path, decompiled_dir)
            
            update_apktool_yml(decompiled_dir)
            modify_manifest(decompiled_dir)
            modify_xml(decompiled_dir)
            modify_styles(decompiled_dir, color_hex, color_name)
            modify_colors(decompiled_dir, color_hex)
            modify_smali(decompiled_dir, color_hex)
            
            # リコンパイル (署名前のAPK)
            unsigned_apk = os.path.join(OUTPUT_DIR, f"unsigned-{color_name}.apk")
            recompile_apk(decompiled_dir, unsigned_apk)
            
            # 署名 (apksignerを使用)
            final_apk_name = f"Origin-Twitter-Neo.{color_name}.v{clean_version}-release.{release_id}.apk"
            final_apk_path = os.path.join(OUTPUT_DIR, final_apk_name)
            
            sign_apk_v2(unsigned_apk, final_apk_path)
            
            # 掃除
            if os.path.exists(unsigned_apk):
                os.remove(unsigned_apk)
            shutil.rmtree(decompiled_dir, ignore_errors=True)
            
            print(f"✅ Successfully created: {final_apk_name}")
            
        except Exception as e:
            print(f"❌ Error processing {color_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*50}")
    print("All color variants processed!")

def decompile_apk(apk_path, output_path):
    print(f"Decompiling APK to: {output_path}")
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    
    cmd = APK_TOOL + ["d", apk_path, "-o", output_path, "--force"] if isinstance(APK_TOOL, list) else [APK_TOOL, "d", apk_path, "-o", output_path, "--force"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"apktool decompile failed:\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    print("✅ Decompilation completed")

def update_apktool_yml(decompiled_path):
    yml_path = os.path.join(decompiled_path, "apktool.yml")
    if os.path.exists(yml_path):
        with open(yml_path, "r", encoding="utf-8") as f:
            yml_data = yaml.safe_load(f)
        doNotCompress = yml_data.get("doNotCompress", [])
        if ".so" not in doNotCompress:
            doNotCompress.append(".so")
        yml_data["doNotCompress"] = doNotCompress
        with open(yml_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(yml_data, f)

def modify_manifest(decompiled_path):
    manifest_path = os.path.join(decompiled_path, "AndroidManifest.xml")
    if not os.path.exists(manifest_path): return
    
    ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    application = root.find('application')
    if application is not None:
        application.set("{http://schemas.android.com/apk/res/android}extractNativeLibs", "true")
        tree.write(manifest_path, encoding="utf-8", xml_declaration=True)

def modify_xml(decompiled_path):
    xml_files = ["res/layout/ocf_twitter_logo.xml", "res/layout/login_toolbar_seamful_custom_view.xml"]
    for xml_file in xml_files:
        file_path = os.path.join(decompiled_path, xml_file)
        if not os.path.exists(file_path): continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("?dynamicColorGray1100", "@color/twitter_blue")
        content = content.replace("@color/gray_1100", "@color/twitter_blue")
        content = re.sub(r"#ff1d9bf0|#ff1da1f2", "@color/twitter_blue", content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def modify_styles(decompiled_path, color_hex, color_name):
    styles_path = os.path.join(decompiled_path, "res/values/styles.xml")
    if not os.path.exists(styles_path): return
    tree = ET.parse(styles_path)
    root = tree.getroot()
    for style in root.findall("style"):
        name = style.get("name", "")
        if name in ["TwitterBase.Dim", "TwitterBase.LightsOut", "TwitterBase.Standard"]:
            for item in style.findall("item"):
                if item.get("name") == "coreColorBadgeVerified": item.text = "@color/blue_500"
        elif name in ["PaletteDim", "PaletteLightsOut", "PaletteStandard"]:
            for item in style.findall("item"):
                if item.get("name") == "abstractColorUnread": item.text = "@color/twitter_blue_opacity_50"
                elif item.get("name") == "abstractColorLink" and name == "PaletteStandard": item.text = "@color/twitter_blue"
        elif name in ["Theme.LaunchScreen"]:
            for item in style.findall("item"):
                if item.get("name") == "windowSplashScreenBackground": item.text = "@color/twitter_blue"
    tree.write(styles_path, encoding="utf-8", xml_declaration=True)

def modify_colors(decompiled_path, color_hex):
    colors_path = os.path.join(decompiled_path, "res/values/colors.xml")
    if not os.path.exists(colors_path): return
    tree = ET.parse(colors_path)
    root = tree.getroot()
    hex_color = f"#ff{color_hex}"
    opacity_map = {
        "twitter_blue": hex_color,
        "deep_transparent_twitter_blue": f"#cc{color_hex}",
        "twitter_blue_opacity_30": f"#4d{color_hex}",
        "twitter_blue_opacity_50": f"#80{color_hex}",
        "twitter_blue_opacity_58": f"#95{color_hex}"
    }
    for color_tag in root.findall("color"):
        name = color_tag.get("name", "")
        if name in opacity_map: color_tag.text = opacity_map[name]
    tree.write(colors_path, encoding="utf-8", xml_declaration=True)

def hex_to_smali(hex_color):
    int_color = int(hex_color, 16)
    smali_int = (int_color ^ 0xFFFFFF) + 1
    smali_value = f"-0x{smali_int:06x}"
    return smali_value.lower()

def modify_smali(decompiled_path, color_hex):
    smali_color = hex_to_smali(color_hex) + "00000000L"
    patterns = {
        re.compile(r"-0xe2641000000000L", re.IGNORECASE): smali_color,
        re.compile(r"0xff1d9bf0L", re.IGNORECASE): f"0xff{color_hex}L",
    }
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

def recompile_apk(decompiled_path, output_apk):
    print(f"Recompiling APK to: {output_apk}")
    cmd = APK_TOOL + ["b", decompiled_path, "-o", output_apk] if isinstance(APK_TOOL, list) else [APK_TOOL, "b", decompiled_path, "-o", output_apk]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Recompilation failed: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)

def find_android_tool(tool_name):
    """Android SDKのビルドツールからツールを探す"""
    android_home = os.environ.get("ANDROID_HOME")
    if not android_home:
        # PATHから探してみる
        return tool_name
    
    build_tools_dir = os.path.join(android_home, "build-tools")
    if not os.path.exists(build_tools_dir):
        return tool_name
    
    # 新しいバージョン順に探す
    versions = sorted(os.listdir(build_tools_dir), reverse=True)
    for version in versions:
        tool_path = os.path.join(build_tools_dir, version, tool_name)
        if os.path.exists(tool_path):
            return tool_path
    
    return tool_name

def sign_apk_v2(unsigned_apk_path, signed_apk_path):
    """
    zipalign -> apksigner の順で処理を行う (V2/V3署名対応)
    """
    print(f"Signing APK: {os.path.basename(unsigned_apk_path)} with apksigner")
    
    # 1. zipalign (最適化)
    # apksignerを使う場合、署名の前に必ずzipalignを行う必要がある
    aligned_apk = unsigned_apk_path + ".aligned"
    zipalign_tool = find_android_tool("zipalign")
    
    print(f"Running zipalign...")
    align_cmd = [zipalign_tool, "-f", "-v", "4", unsigned_apk_path, aligned_apk]
    
    try:
        subprocess.run(align_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ zipalign failed: {e.stderr}")
        # 失敗した場合でも、とりあえず署名を試みるフォールバック（推奨されない）
        shutil.copy(unsigned_apk_path, aligned_apk)

    # 2. apksigner (署名)
    apksigner_tool = find_android_tool("apksigner")
    
    print(f"Running apksigner...")
    sign_cmd = [
        apksigner_tool, "sign",
        "--ks", KEYSTORE_PATH,
        "--ks-pass", f"pass:{STOREPASS}",
        "--ks-key-alias", ALIAS,
        "--key-pass", f"pass:{KEYPASS}",
        "--out", signed_apk_path,
        aligned_apk
    ]
    
    result = subprocess.run(sign_cmd, capture_output=True, text=True)
    
    # 中間ファイルを削除
    if os.path.exists(aligned_apk):
        os.remove(aligned_apk)

    if result.returncode != 0:
        print(f"❌ apksigner failed: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, sign_cmd)
    
    print(f"✅ Signed APK successfully: {os.path.basename(signed_apk_path)}")

if __name__ == "__main__":
    main()

