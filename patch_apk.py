import os
import subprocess
import xml.etree.ElementTree as ET
import re
import glob
import shutil
import yaml
import zipfile


APK_TOOL = "apktool"
OUTPUT_DIR = "patched_apks"
APK_VERSION = None  # ダウンロードAPKから取得する

AAPT2 = "aapt2"
KEYSTORE_PATH = "./origin-twitter.keystore"
ALIAS = "origin"
STOREPASS = "123456789"
KEYPASS = "123456789"

# カラーコードと名前のマッピング
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

# 1. GitHub リリースバージョン（GitHub から取得した VERSION 環境変数を使用）
apk_version = os.getenv('VERSION')  # GitHub Actions から VERSION 環境変数を取得
apk_file_name = f"twitter-piko-v{apk_version}.apk"  # 正しいファイル名
apk_path = f"downloads/{apk_file_name}"  # APK のパス
decompiled_path = f"downloads/{apk_file_name}_decompiled"  # デコンパイルされたファイルのパス

print(f"APK Path: {apk_path}")  # デバッグ用ログ

def decompile_apk(apk_path, output_path):
    print(f"Checking if APK file exists: {apk_path}")
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK file not found: {apk_path}")
    
    subprocess.run([APK_TOOL, "d", apk_path, "-o", output_path, "--force"], check=True)

def patch_apk(apk_path):
    # APKのデコンパイル
    print(f"Decompiling APK: {apk_path}")
    decompile_apk(apk_path, decompiled_path)

# 2. バージョン番号を取得
def get_apk_version(apk_path):
    global APK_VERSION
    # ファイル名からバージョン番号を取得
    match = re.search(r"twitter-piko-v(\d+\.\d+\.\d+)-release.0.apk", apk_path)
    if match:
        APK_VERSION = match.group(1)
    else:
        APK_VERSION = "unknown"
    print(f"Detected APK Version: {APK_VERSION}")

# 3. XMLの変更
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

# 4. styles.xmlの修正
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

# 5. colors.xmlの修正
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

# 6. smaliの修正
def hex_to_smali(hex_color):
    """16進カラーコード (RRGGBB) を smali の負の16進数表記 (-0xXXXXXX00000000L) に変換する"""
    int_color = int(hex_color, 16)  # 16進数カラーコードを整数に変換 (0xRRGGBB)
    # smali の負数表記にするために 2の補数を取る (符号付き 32-bit に拡張)
    smali_int = (int_color ^ 0xFFFFFF) + 1  # 1の補数を取って+1（2の補数）
    # smali フォーマットに整形（小文字化）
    smali_value = f"-0x{smali_int:06x}"
    return smali_value.lower()

def modify_smali(decompiled_path, color):
    """デコンパイルされた全 `.smali` ファイルを対象に `-0xe2641000000000L` を新しい値に置換する"""
    smali_color = hex_to_smali(color) + "00000000L"  # `-0xXXXXXX00000000L` に変換
    
    # `-0xe2641000000000L` に厳密にマッチする正規表現
    pattern = re.compile(r"-0xe2641000000000L", re.IGNORECASE)
    
    print(f"Scanning all .smali files under: {decompiled_path}")
    for root, _, files in os.walk(decompiled_path):  # `decompiled_path` 全体を探索
        for file in files:
            if file.endswith(".smali"):  # `.smali` ファイルのみ処理
                smali_path = os.path.join(root, file)
                print(f"Processing: {smali_path}")
                with open(smali_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # `-0xe2641000000000L` のみを新しい `-0xXXXXXX00000000L` に置換
                new_content = pattern.sub(smali_color, content)

                if new_content != content:  # 変更があった場合のみ書き込み
                    with open(smali_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Modified: {smali_path}")
                    
# 7. APKの再構築と署名

def get_zipalign_path():
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not android_home:
        raise FileNotFoundError("ANDROID_HOME or ANDROID_SDK_ROOT が設定されていません。")

    build_tools_dir = os.path.join(android_home, "build-tools")
    versions = sorted(os.listdir(build_tools_dir), reverse=True)

    for version in versions:
        zipalign_path = os.path.join(build_tools_dir, version, "zipalign")
        if os.path.exists(zipalign_path):
            return zipalign_path

    raise FileNotFoundError("zipalign が見つかりませんでした。")

def get_apksigner_path():
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not android_home:
        raise FileNotFoundError("ANDROID_HOME or ANDROID_SDK_ROOT が設定されていません。")

    build_tools_dir = os.path.join(android_home, "build-tools")
    versions = sorted(os.listdir(build_tools_dir), reverse=True)

    for version in versions:
        apksigner_path = os.path.join(build_tools_dir, version, "apksigner")
        if os.path.exists(apksigner_path):
            return apksigner_path

    raise FileNotFoundError("apksigner が見つかりませんでした。")

def recompile_apk(decompiled_path, output_apk):
    """APK を再構築"""
    subprocess.run([APK_TOOL, "b", decompiled_path, "-o", output_apk], check=True)

def optimize_resources_arsc(apk_path):
    """resources.arsc を適切に圧縮して 4バイト境界に配置"""
    optimized_apk = apk_path + ".optimized"

    subprocess.run([
        AAPT2, "optimize",
        "--shorten-resource-paths",
        "--enable-sparse-encoding",
        "--deduplicate-entry-values",
        apk_path,
        "-o", optimized_apk
    ], check=True)

    # 置き換え
    shutil.move(optimized_apk, apk_path)
    print(f"✅ resources.arsc を最適化しました: {apk_path}")

def align_resources_arsc(apk_path):
    """resources.arsc を 4バイト境界に配置"""
    zipalign_path = get_zipalign_path()
    aligned_apk = apk_path + ".aligned"

    # zipalign で 4バイト境界に調整
    subprocess.run([zipalign_path, "-v", "4", apk_path, aligned_apk], check=True)
    
    # 置き換え
    shutil.move(aligned_apk, apk_path)
    print(f"✅ resources.arsc を 4バイト境界に配置しました: {apk_path}")

def sign_apk(apk_path):
    """APK を V1, V2, V3 署名して zipalign する"""
    zipalign_path = get_zipalign_path()
    apksigner_path = get_apksigner_path()

    # resources.arsc の整列と最適化
    optimize_resources_arsc(apk_path)
    align_resources_arsc(apk_path)

    # V1 署名 (jarsigner)
    subprocess.run([
        "jarsigner",
        "-verbose",
        "-sigalg", "SHA256withRSA",
        "-digestalg", "SHA-256",
        "-keystore", KEYSTORE_PATH,
        "-storepass", STOREPASS,
        "-keypass", KEYPASS,
        apk_path,
        ALIAS
    ], check=True)

    # V2, V3 署名 (apksigner)
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

    # 署名の確認
    subprocess.run([apksigner_path, "verify", "--print-certs", apk_path], check=True)

    return apk_path


# 8. 全プロセスの実行
def patch_apk(apk_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    get_apk_version(apk_path)

    for color, name in THEME_COLORS.items():
        decompiled_path = f"{apk_path}_decompiled_{color}"
        patched_apk = os.path.join(OUTPUT_DIR, f"Origin-Twitter.{name}.v{APK_VERSION}-release.0.apk")  # バージョン番号を追加
        
        decompile_apk(apk_path, decompiled_path)
        modify_xml(decompiled_path)
        modify_styles(decompiled_path)
        modify_colors(decompiled_path, color)
        modify_smali(decompiled_path, color)
        recompile_apk(decompiled_path, patched_apk)
        sign_apk(patched_apk)
        print(f"Generated: {patched_apk}")

# 実行部分
if __name__ == "__main__":
    print(f"Detected APK Version: {apk_version}")
    patch_apk(apk_path)