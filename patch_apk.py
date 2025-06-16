import os
import subprocess
import xml.etree.ElementTree as ET
import re
import shutil
import zipfile
import tempfile

APK_TOOL = "apktool"
OUTPUT_DIR = "patched_apks"
APK_VERSION = None 
AAPT2 = "aapt2"
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

apk_version = os.getenv('CRIMERA_TAG')  
apk_file_name = f"twitter-piko-v{apk_version}.apk" 
apk_path = f"downloads/{apk_file_name}"  

print(f"APK Path: {apk_path}")

def decompile_apk(apk_path, output_path):
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK file not found: {apk_path}")
    subprocess.run([APK_TOOL, "d", apk_path, "-o", output_path, "--force"], check=True)

def get_apk_version(apk_path):
    global APK_VERSION
    match = re.search(r"twitter-piko-v(\d+\.\d+\.\d+)-release.0.apk", apk_path)
    APK_VERSION = match.group(1) if match else "unknown"
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
    if not os.path.exists(styles_path): return
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
        elif name == "Theme.LaunchScreen":
            for item in style.findall("item"):
                if item.get("name") == "windowSplashScreenBackground":
                    item.text = "@color/twitter_blue"
    tree.write(styles_path, encoding="utf-8", xml_declaration=True)

def modify_colors(decompiled_path, color):
    colors_path = os.path.join(decompiled_path, "res/values/colors.xml")
    if not os.path.exists(colors_path): return
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
    for root_dir, _, files in os.walk(decompiled_path):
        for file in files:
            if file.endswith(".smali"):
                smali_path = os.path.join(root_dir, file)
                with open(smali_path, "r", encoding="utf-8") as f:
                    content = f.read()
                original = content
                for pattern, repl in patterns.items():
                    content = pattern.sub(repl, content)
                if content != original:
                    with open(smali_path, "w", encoding="utf-8") as f:
                        f.write(content)

def get_zipalign_path():
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    for version in sorted(os.listdir(os.path.join(sdk, "build-tools")), reverse=True):
        path = os.path.join(sdk, "build-tools", version, "zipalign")
        if os.path.exists(path):
            return path
    raise FileNotFoundError("zipalign not found")

def get_apksigner_path():
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    for version in sorted(os.listdir(os.path.join(sdk, "build-tools")), reverse=True):
        path = os.path.join(sdk, "build-tools", version, "apksigner")
        if os.path.exists(path):
            return path
    raise FileNotFoundError("apksigner not found")

def recompile_apk(decompiled_path, output_apk):
    subprocess.run([APK_TOOL, "b", decompiled_path, "-o", output_apk], check=True)

def optimize_resources_arsc(apk_path):
    optimized_apk = apk_path + ".optimized"
    subprocess.run([AAPT2, "optimize", "--shorten-resource-paths", "--enable-sparse-encoding",
                    "--deduplicate-entry-values", apk_path, "-o", optimized_apk], check=True)
    shutil.move(optimized_apk, apk_path)

def align_resources_arsc(apk_path):
    zipalign_path = get_zipalign_path()
    aligned_apk = apk_path + ".aligned"
    subprocess.run([zipalign_path, "-v", "4", apk_path, aligned_apk], check=True)
    shutil.move(aligned_apk, apk_path)

def sign_apk(apk_path):
    optimize_resources_arsc(apk_path)
    align_resources_arsc(apk_path)
    apksigner = get_apksigner_path()
    subprocess.run([apksigner, "sign", "--ks", KEYSTORE_PATH,
                    "--ks-pass", f"pass:{STOREPASS}",
                    "--ks-key-alias", ALIAS,
                    "--key-pass", f"pass:{KEYPASS}",
                    "--v1-signing-enabled", "true",
                    "--v2-signing-enabled", "true",
                    "--v3-signing-enabled", "true",
                    "--v4-signing-enabled", "false",
                    apk_path], check=True)
    subprocess.run([apksigner, "verify", "--print-certs", apk_path], check=True)

def restore_libs(original_apk_path, rebuilt_apk_path):
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        
        with zipfile.ZipFile(original_apk_path, 'r') as zip_ref:
            lib_files = [f for f in zip_ref.namelist() if f.startswith("lib/") and f.endswith(".so")]
            zip_ref.extractall(temp_dir, lib_files)

        with zipfile.ZipFile(rebuilt_apk_path, 'r') as zip_read:
            entries = [item for item in zip_read.infolist() if not item.filename.startswith("lib/")]
            with zipfile.ZipFile(rebuilt_apk_path + ".tmp", 'w') as zip_write:
                for item in entries:
                    zip_write.writestr(item, zip_read.read(item.filename))

        shutil.move(rebuilt_apk_path + ".tmp", rebuilt_apk_path)
        
        with zipfile.ZipFile(rebuilt_apk_path, 'a') as zip_write:
            for root, _, files in os.walk(os.path.join(temp_dir, "lib")):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, temp_dir)
                    zip_write.write(full_path, relative_path)

    print(f"✅ Cleaned and restored native libraries into: {rebuilt_apk_path}")

def patch_apk(apk_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    get_apk_version(apk_path)
    for color, name in THEME_COLORS.items():
        decompiled_path = f"{apk_path}_decompiled_{color}"
        patched_apk = os.path.join(OUTPUT_DIR, f"Origin-Twitter.{name}.v{APK_VERSION}-release.0.apk")
        decompile_apk(apk_path, decompiled_path)
        modify_xml(decompiled_path)
        modify_styles(decompiled_path)
        modify_colors(decompiled_path, color)
        modify_smali(decompiled_path, color)
        recompile_apk(decompiled_path, patched_apk)
        restore_libs(apk_path, patched_apk)
        sign_apk(patched_apk)
        print(f"✅ Generated: {patched_apk}")

if __name__ == "__main__":
    print(f"Detected APK Version: {apk_version}")
    patch_apk(apk_path)
