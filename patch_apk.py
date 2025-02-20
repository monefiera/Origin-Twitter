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

# Colorcode & Colorname Mapping
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

# 1. GitHub release version (using the VERSION environment variable obtained from GitHub)
apk_version = os.getenv("CRIMERA_TAG")  
apk_file_name = f"twitter-piko-v{apk_version}.apk"  
apk_path = f"downloads/{apk_file_name}" 
decompiled_path = f"downloads/{apk_file_name}_decompiled"  

print(f"APK Path: {apk_path}")  

def decompile_apk(apk_path, output_path):
    print(f"Checking if APK file exists: {apk_path}")
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK file not found: {apk_path}")
    
    subprocess.run([APK_TOOL, "d", apk_path, "-o", output_path, "--force"], check=True)

def patch_apk(apk_path):
    
    print(f"Decompiling APK: {apk_path}")
    decompile_apk(apk_path, decompiled_path)

# 2. Get version number
def get_apk_version(apk_path):
    global APK_VERSION
    # Get version number from file name
    match = re.search(r"twitter-piko-v(\d+\.\d+\.\d+)-release.0.apk", apk_path)
    if match:
        APK_VERSION = match.group(1)
    else:
        APK_VERSION = "unknown"
    print(f"Detected APK Version: {APK_VERSION}")

# 3. Change some XML
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

# 4. Modding styles.xml
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

# 5. Modding colors.xml
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

# 6. Modding smali
def hex_to_smali(hex_color):
    """Convert hex color code (RRGGBB) to smali negative hex notation (-0xXXXXXX000000000000L)"""
    int_color = int(hex_color, 16) 
    # Take 2's complement to make smali negative notation (extended to signed 32-bit)
    smali_int = (int_color ^ 0xFFFFFF) + 1  
    # Formatted (lowercased) in smali format
    smali_value = f"-0x{smali_int:06x}"
    return smali_value.lower()

def modify_smali(decompiled_path, color):
    """Replace `-0xe2641000000000L` with the new value for all decompiled `.smali` files"""
    smali_color = hex_to_smali(color) + "00000000L" 
    
    # Regular expression matching `-0xe2641000000000L` exactly
    pattern = re.compile(r"-0xe2641000000000L", re.IGNORECASE)
    
    print(f"Scanning all .smali files under: {decompiled_path}")
    for root, _, files in os.walk(decompiled_path):  
        for file in files:
            if file.endswith(".smali"):  
                smali_path = os.path.join(root, file)
                print(f"Processing: {smali_path}")
                with open(smali_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace only `-0xe2641000000000L` with new `-0xXXXXXX000000000000L`
                new_content = pattern.sub(smali_color, content)

                if new_content != content:  
                    with open(smali_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Modified: {smali_path}")
                    
# 7. APK ReBuild & Sign

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

    raise FileNotFoundError("zipalign was not found.")

def optimize_resources_arsc(apk_path):
    """Properly compress resources.arsc and place it on a 4-byte boundary"""
    optimized_apk = apk_path + ".optimized"

    subprocess.run([
        AAPT2, "optimize",
        "--shorten-resource-paths",
        "--enable-sparse-encoding",
        "--deduplicate-entry-values",
        "--collapse-keystrings", 
        apk_path,
        "-o", optimized_apk
    ], check=True)

    shutil.move(optimized_apk, apk_path)
    print(f"✅ Optimized resources.arsc : {apk_path}")

def align_resources_arsc(apk_path):

    zipalign_path = get_zipalign_path()
    aligned_apk = apk_path + ".aligned"

    # Place resources.arsc on a 4-byte boundary
    subprocess.run([zipalign_path, "-v", "4", apk_path, aligned_apk], check=True)
    

    shutil.move(aligned_apk, apk_path)
    print(f"✅ resources.arsc is now placed on a 4-byte boundary : {apk_path}")

def sign_apk(apk_path):
    zipalign_path = get_zipalign_path()
    apksigner_path = get_apksigner_path()

    # ✅ Run zipalign and optimize with AAPT2 optimize
    align_resources_arsc(apk_path)
    optimize_resources_arsc(apk_path)

    # ✅ V1 Sign (jarsigner)
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

    # ✅ V2 & V3 Sign (apksigner)
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

    # ✅ Signature Verification
    subprocess.run([apksigner_path, "verify", "--print-certs", apk_path], check=True)

    return apk_path


# 8. Execution of all processes
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

# Executable part
if __name__ == "__main__":
    print(f"Detected APK Version: {apk_version}")
    patch_apk(apk_path)
