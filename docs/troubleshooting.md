# Troubleshooting.md
## Display Problems
We noticed when we first got the device that the framerate is low, but it's because we are 
writing the code in Python.

## Touchproblems
We noticed that the touchscreen is very sensitive about where you put your finger to swipe and we fixed the issue by scrolling with our finger in the bottom right of the screen.

## Wi-Fi problems
We noticed it was hard to keep track of what Wi-Fi the device was connected to so we added a Wi-Fi credentials tab to keep track of it easily.

## Å, ä and ö not shown
The built-in fonts only contain ASCII characters, so Swedish stop names were missing letters. fonts.py adds å, ä, ö and a few other letters on top of the built-in fonts, including the Danish æ and ø used by Øresundståg (København).

## SyntaxError in main.py after deploy
Deploy only flashes the first 256 KB of the file system (`VFS_DEPLOY_SIZE` in [platformio/deploy.py](../platformio/deploy.py#26)). If all files in `project/` take more space than that, the last files are cut off and the device reads broken code, which shows as a SyntaxError on a line that does not exist. Keep `project/` small; this is why fonts.py only contains å, ä, ö and a few other letters. Increasing the `VFS_DEPLOY_SIZE` will also work but will lead to longer upload times.

## Memory problems
When connecting the trafiklab API to the device we noticed that it crashed due to the amount of stops there was, to fix it we stored the stops in Karlskrona to a file that the device then uses to get all the needed stops.
