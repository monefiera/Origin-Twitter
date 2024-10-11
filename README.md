# Origin-Twitter
![GitHub Downloads](https://img.shields.io/github/downloads/monefiera/Origin-Twitter/total?color=green&style=for-the-badge&logo=github)
![GitHub Issues](https://img.shields.io/github/issues/monefiera/Origin-Twitter?style=for-the-badge&logo=github)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/monefiera/Origin-Twitter?style=for-the-badge&logo=github)<br>
My Personal Build apk for JP & Colorful Lovers<br>

## About this
Mod apk with 10 color themes and recaptured all Twitter elements in Japanese<br>

### Important Section
[Piko Revanced Patch](https://github.com/crimera/piko) is NOT INCLUDED in this builds.<br>
Please patch it yourself to use [Revanced Manager](https://github.com/ReVanced/revanced-manager) or [Revancify](https://github.com/decipher3114/Revancify).<br>
I recommend Revancify because it is less error than RVManager.<br>
LSPatch※ can inject [Hachidori](https://github.com/Xposed-Modules-Repo/com.twifucker.hachidori) with non-root devices(but not recommended).<br>
※At 1st, I had written [JingMatrix repository](https://github.com/JingMatrix/LSPatch), but after verification it was not possible, so I'm taking it down.<br>
I'm currently looking for a patchable LSPatch.<br>

## Using Tools
・[AntiSplit-M](https://github.com/AbdurazaaqMohammed/AntiSplit-M) convert [apkmirror's apkm](https://www.apkmirror.com/apk/x-corp/twitter/) to apk<br>
・[APKToolGUI](https://github.com/AndnixSH/APKToolGUI) & [Virtual Studio Code](https://code.visualstudio.com/) to edit any resources<br>
・[MT Manager](https://mt2.cn) to sign apk<br>
・[Hex To Smali Online Converter](https://pantrif.github.io/HexToSmaliConverter/#) to analyze some colors<br>

## State changes in original apk
- Bring Back Twitter※ without relying on piko patch
※Fix ugly alterations(including blands) by Elon Musk<br>
- Replaced Post with Tweet(but only EN & JP)
- Change Color Theme but it needs reinstall

## Color Menu
You can choose from several color themes like Twitter for Web<br>
①Original Twitter's Colors<br>
💧Origin Blue(#1d9bf0)<br>
⭐Star Gold(#fed400)<br>
🌸Sakura Red(#f91880)<br>
🐙Octopus Purple(#7856ff)<br>
🔥Flare Orange(#ff7a00)<br>
🥑Avocado Green(#31c88e)<br>
And also you can choose my best colors<br>
②FIERA's Additional Colors<br>
🌹Crimsonate(#c20024)<br>
💎Izumo Lazurite(#1e50a2)<br>
☁Monotone(#808080)<br>
🩷MateChan Pink(#ffadc0)<br>

## How to make colorful mod?(for piko developers)
<details>
This may be a little confusing, but please use it as hints for a complete color patch implementation and Bring Back Twitter fix.<br>
This covers of piko's Bring Back Twitter patch partially.<br>
<br>
1: Replace “?dynamicColorGray1100” or “@color/gray_1100” in the file with “@color/twitter_blue”.<br>  
- res\layout\ocf_twitter_logo.xml
- res\layout\channels_toolbar_main.xml
- res\layout\login_toolbar_seamful_custom_view.xml
- style name="Theme.LaunchScreen"'s [windowSplashScreenBackground] in res\values\styles.xml
- [ic_launcher_background] in res\values\colors.xml<br>

2: Replace “#ff1d9bf0” with “@color/twitter_blue” in all files in the res folder except (res\values\)colors.xml and styles.xml.<br>

3: In styles.xml, change value of “coreColorBadgeVerified” for **<style name="TwitterBase.Dim" parent="@style/PaletteDim">**, **<style name="TwitterBase.LightsOut" parent="@style/PaletteLightsOut">** and **<style name="TwitterBase.Standard" parent="@style/PaletteStandard">** to @color/blue_500.<br>

4: In styles.xml, replace “abstractColorUnread” values of **<style name="PaletteDim" parent="@style/HorizonColorPaletteDark">**, **<style name="PaletteLightsOut" parent="@style/HorizonColorPaletteDark">** and **<style name="PaletteStandard" parent="@style/HorizonColorPaletteLight">** to @color/twitter_blue_opacity_50.<br>
And change the value of “abstractColorLink” in **<style name=“PaletteStandard” parent=“@style/HorizonColorPaletteLight”>** to @color/twitter_blue.<br>

At this point, the preparation is complete.<br>

5: In color.xml, change “badge_verified” value to @color/blue_500 and “twitter_blue” to #ff (any color code).<br>
In addition, change “deep_transparent_twitter_blue”, “twitter_blue_opacity_30”, “twitter_blue_opacity_50”, and “twitter_blue_opacity_58”, paying attention to # and the first two characters.<br>

6: Find two -0xE26410 values in the smali file and replace them with the FF (color code) specified in color.xml.<br>
Needless to say, note that it is necessary to convert to smali value. The location of the two smali files with hidden color codes varies from version to version, but the last two letters of the file name are the same, like yxx.smali and rxx.smali.<br>

The following is a brief description of what is done in each section.<br>
<details>
At 1's login_toolbar_seamful_custom_view.xml defines the color of the bird when first logging into Twitter. This and other parts of this work complete elements that Bring Back Twitter has not been able to return to.<br>
At 2, the work is to change the parts (such as the camera icon on the tweet screen) whose colors do not change even if the procedures described in 3 and below are performed.<br>
At 3 and beginning of 5, replace work is being done to change the badge color back to blue. This is because the same color as the theme may be difficult to recognize.<br>
At 4, the color of notification column is treated to be linked to the theme. Also, only in the light theme, the link color is not @color/twitter_blue, so the color is reflected by replacing it.<br>
</details>
</details>

## Credits
・[Twitter Inc.](https://twitter.com)：but it's gone…<br>
・[Swakshan](https://github.com/Swakshan) & [Mufti Faishal](https://twitter.com/Mufti96)：Help to smali color value<br>
・[Web色見本 原色大辞典](https://www.colordic.org)：Help to Find any colors<br>
・[Risa Yuzuki](https://yuzu-risa.com)：The name holder of [Crimsonate](https://www.youtube.com/watch?v=LuN5t8xIcKM), which is my most favorite song<br>
・[MateChan](https://matechan.com)：One of color is for him<br>
・And Another One Person...<br>
