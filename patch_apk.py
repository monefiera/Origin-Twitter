import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

# ====== Settings ======
APK_TOOL = "apktool"
KEYSTORE_PATH = "./origin-twitter.keystore"
ALIAS = "origin"
STOREPASS = "123456789"
KEYPASS = "123456789"
OUTPUT_DIR = "patched_apks"

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

apk_version_env = os.getenv('CRIMERA_TAG')
apk_file_name = f"twitter-piko-v{apk_version_env}.apk"
apk_path = f"downloads/{apk_file_name}"


# ====== Utility ======

def get_sdk_tool(tool_name):
    sdk_path = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")
    for version in sorted(os.listdir(os.path.join(sdk_path, "build-tools")), reverse=True):
        tool_path = os.path.join(sdk_path, "build-tools", version, tool_name)
        if os.path.isfile(tool_path):
            return tool_path
    raise FileNotFoundError(f"{tool_name} not found in build-tools")

def extract_apk_version(apk_name):
    match = re.search(r"v(\d+\.\d+\.\d+)", apk_name)
    return match.group(1) if match else "unknown"


# ====== APK Handling ======

def decompile_apk(input_apk, output_dir):
    subprocess.run([APK_TOOL, "d", input_apk, "-o", output_dir, "--force"], check=True)

def recompile_apk(input_dir, output_apk):
    subprocess.run([APK_TOOL, "b", input_dir, "-o", output_apk], check=True)

def inject_native_libs_to_apk(apk_path, original_apk):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Extract lib files from original APK
        with zipfile.ZipFile(original_apk, 'r') as orig_zip:
            for file in orig_zip.namelist():
                if file.startswith("lib/") and file.endswith(".so"):
                    target_path = os.path.join(tmpdir, file)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "wb") as f:
                        f.write(orig_zip.read(file))

        # Repack ZIP as APK
        fixed_apk = apk_path.replace(".apk", "_fixed.apk")
        shutil.make_archive(fixed_apk.replace(".apk", ""), 'zip', tmpdir)
        shutil.move(fixed_apk.replace(".apk", "") + ".zip", fixed_apk)
        return fixed_apk

def align_apk(apk_file):
    zipalign = get_sdk_tool("zipalign")
    aligned_apk = apk_file + ".aligned"
    subprocess.run([zipalign, "-v", "4", apk_file, aligned_apk], check=True)
    shutil.move(aligned_apk, apk_file)

def sign_apk(apk_file):
    apksigner = get_sdk_tool("apksigner")
    subprocess.run([
        apksigner, "sign",
        "--ks", KEYSTORE_PATH,
        "--ks-pass", f"pass:{STOREPASS}",
        "--ks-key-alias", ALIAS,
        "--key-pass", f"pass:{KEYPASS}",
        "--v1-signing-enabled", "true",
        "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true",
        "--v4-signing-enabled", "false",
        apk_file
    ], check=True)


# ====== Modding Functions ======

def modify_xmls(base_path):
    targets = [
        "res/layout/ocf_twitter_logo.xml",
        "res/layout/login_toolbar_seamful_custom_view.xml"
    ]
    for rel in targets:
        path = os.path.join(base_path, rel)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("?dynamicColorGray1100", "@color/twitter_blue")
            content = content.replace("@color/gray_1100", "@color/twitter_blue")
            content = re.sub(r"#ff1d9bf0|#ff1da1f2", "@color/twitter_blue", content)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

def modify_styles(base_path):
    style_path = os.path.join(base_path, "res/values/styles.xml")
    if not os.path.isfile(style_path): return
    tree = ET.parse(style_path)
    root = tree.getroot()

    for style in root.findall("style"):
        name = style.get("name", "")
        for item in style.findall("item"):
            if name.startswith("TwitterBase") and item.get("name") == "coreColorBadgeVerified":
                item.text = "@color/blue_500"
            if name.startswith("Palette"):
                if item.get("name") == "abstractColorUnread":
                    item.text = "@color/twitter_blue_opacity_50"
                elif item.get("name") == "abstractColorLink" and name == "PaletteStandard":
                    item.text = "@color/twitter_blue"
            if name == "Theme.LaunchScreen" and item.get("name") == "windowSplashScreenBackground":
                item.text = "@color/twitter_blue"
    tree.write(style_path, encoding="utf-8", xml_declaration=True)

def modify_colors(base_path, color):
    color_path = os.path.join(base_path, "res/values/colors.xml")
    if not os.path.isfile(color_path): return
    tree = ET.parse(color_path)
    root = tree.getroot()

    hex_color = f"#ff{color}"
    opacity_map = {
        "twitter_blue": hex_color,
        "deep_transparent_twitter_blue": f"#cc{color}",
        "twitter_blue_opacity_30": f"#4d{color}",
        "twitter_blue_opacity_50": f"#80{color}",
        "twitter_blue_opacity_58": f"#95{color}"
    }

    for tag in root.findall("color"):
        name = tag.get("name", "")
        if name in opacity_map:
            tag.text = opacity_map[name]
    tree.write(color_path, encoding="utf-8", xml_declaration=True)

def modify_smali(base_path, color):
    smali_replacements = {
        re.compile(r"-0xe2641000000000L", re.IGNORECASE): f"-0x{((int(color, 16) ^ 0xFFFFFF)+1):06x}00000000L",
        re.compile(r"0xff1d9bf0L", re.IGNORECASE): f"0xff{color}L"
    }
    for root_dir, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".smali"):
                path = os.path.join(root_dir, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                original = content
                for pattern, repl in smali_replacements.items():
                    content = pattern.sub(repl, content)
                if content != original:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)


# ====== Main Patching Logic ======

def patch_apk(original_apk):
    version = extract_apk_version(original_apk)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for hex_color, name in THEME_COLORS.items():
        print(f"🖌️ Patching theme: {name}")
        decompiled_dir = f"{original_apk}_decompiled_{name}"
        output_apk = os.path.join(OUTPUT_DIR, f"Origin-Twitter.{name}.v{version}-release.0.apk")

        decompile_apk(original_apk, decompiled_dir)
        modify_xmls(decompiled_dir)
        modify_styles(decompiled_dir)
        modify_colors(decompiled_dir, hex_color)
        modify_smali(decompiled_dir, hex_color)
        recompile_apk(decompiled_dir, output_apk)
        fixed_apk = inject_native_libs_to_apk(output_apk, original_apk)
        align_apk(fixed_apk)
        sign_apk(fixed_apk)
        print(f"✅ Patched: {fixed_apk}")


# ====== Entry Point ======

if __name__ == "__main__":
    print(f"🔧 Processing APK: {apk_path}")
    patch_apk(apk_path)
