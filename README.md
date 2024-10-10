# Origin-Twitter
My Personal Build apk for JP & Colorful Lovers  

## About this
Mod apk with 10 color themes and recaptured all Twitter elements in Japanese  

### Important Section
[Piko Revanced Patch](https://github.com/crimera/piko) is NOT INCLUDED in this builds.  
Please patch it yourself to use Revanced Manager or Revancify.  
LSPatch※ can inject [Hachidori](https://github.com/Xposed-Modules-Repo/com.twifucker.hachidori) with non-root devices(but not recommended).  
※At 1st, I had written [JingMatrix repository](https://github.com/JingMatrix/LSPatch), but after verification it was not possible, so I'm taking it down.   
I'm currently looking for a patchable LSPatch.  

## Using Tools
・[AntiSplit-M](https://github.com/AbdurazaaqMohammed/AntiSplit-M) convert [apkmirror's apkm](https://www.apkmirror.com/apk/x-corp/twitter/) to apk  
・[APKToolGUI](https://github.com/AndnixSH/APKToolGUI) & [Virtual Studio Code](https://code.visualstudio.com/) to edit any resources  
・[MT Manager](https://mt2.cn) to sign apk  
・[Hex To Smali Online Converter](https://pantrif.github.io/HexToSmaliConverter/#) to analyze some colors  

## State changes in original apk
- Bring Back Twitter※ without relying on piko patch
※Fix ugly alterations(including blands) by Elon Musk
- Replaced Post with Tweet
- Change Color Theme but it needs reinstall

## Color Menu
You can choose from several color themes like Twitter for Web  
①Original Twitter's Colors  
💧Origin Blue(#1d9bf0)  
⭐Star Gold(#fed400)  
🌸Sakura Red(#f91880)  
🐙Octopus Purple(#7856ff)  
🔥Flare Orange(#ff7a00)  
🥑Avocado Green(#00ba7c)  
And also you can choose my best colors  
②FIERA's Additional Colors  
🌹Crimsonate(#c20024)  
💎Izumo Lazurite(#1e50a2)  
☁Monotone(#808080)  
🩷MateChan Pink(#ffadc0)  

## How to make colorful mod?(for therealswak & piko developers)
<details>
This may be a little confusing, but please use it as hints for a complete color patch implementation and Bring Back Twitter fix.  
This covers of piko's Bring Back Twitter patch partially.  
1: Replace “?dynamicColorGray1100” or “@color/gray_1100” in the file with “@color/twitter_blue”.  
- res\layout\ocf_twitter_logo.xml
- res\layout\channels_toolbar_main.xml
- res\layout\login_toolbar_seamful_custom_view.xml
- style name="Theme.LaunchScreen"'s [windowSplashScreenBackground] in res\values\styles.xml
- [ic_launcher_background] in res\values\colors.xml

2: Replace “#ff1d9bf0” with “@color/twitter_blue” in all files in the res folder except (res\values\)colors.xml and styles.xml.  

3: In styles.xml, change value of “coreColorBadgeVerified” for **<style name="TwitterBase.Dim" parent="@style/PaletteDim">**, **<style name="TwitterBase.LightsOut" parent="@style/PaletteLightsOut">** and **<style name="TwitterBase.Standard" parent="@style/PaletteStandard">** to @color/blue_500.  

4: In styles.xml, replace “abstractColorUnread” values of **<style name="PaletteDim" parent="@style/HorizonColorPaletteDark">**, **<style name="PaletteLightsOut" parent="@style/HorizonColorPaletteDark">** and **<style name="PaletteStandard" parent="@style/HorizonColorPaletteLight">** to @color/twitter_blue_opacity_50.  
And change the value of “abstractColorLink” in **<style name=“PaletteStandard” parent=“@style/HorizonColorPaletteLight”>** to @color/twitter_blue.  

At this point, the preparation is complete.  
5: In color.xml, change “badge_verified” value to @color/blue_500 and “twitter_blue” to #ff (any color code).  
In addition, change “deep_transparent_twitter_blue”, “twitter_blue_opacity_30”, “twitter_blue_opacity_50”, and “twitter_blue_opacity_58”, paying attention to # and the first two characters. 

6: Find two -0xE26410 values in the smali file and replace them with the FF (color code) specified in color.xml.  
Needless to say, note that it is necessary to convert to smali value. The location of the two smali files with hidden color codes varies from version to version, but the last two letters of the file name are the same, like yxx.smali and rxx.smali.　 

The following is a brief description of what is done in each section.    
<details>
At 1's login_toolbar_seamful_custom_view.xml defines the color of the bird when first logging into Twitter. This and other parts of this work complete elements that Bring Back Twitter has not been able to return to.  
At 2, the work is to change the parts (such as the camera icon on the tweet screen) whose colors do not change even if the procedures described in 3 and below are performed.  
At 3 and beginning of 5, replace work is being done to change the badge color back to blue. This is because the same color as the theme may be difficult to recognize.    
At 4, the color of notification column is treated to be linked to the theme. Also, only in the light theme, the link color is not @color/twitter_blue, so the color is reflected by replacing it.  
</details>
</details>

## Credits
・[Twitter Inc.](https://twitter.com)：but it's gone…  
・[Web色見本 原色大辞典](https://www.colordic.org)：Help to Find any colors)  
・[Risa Yuzuki](https://yuzu-risa.com)：[Crimsonate](https://www.youtube.com/watch?v=LuN5t8xIcKM) name holder which is one of my most favorite song  
・[MateChan](https://matechan.com)：One of color is for him  
・And Another One Person I loved...   
