# Troubleshooting.md
 # Display Problems
We noticed when we first got the device that the framerate is low, but it's because we are 
writing the code in Python.

 # Touchproblems
We noticed that the touchscreen is very sensitive about where you put your finger to swipe and we fixed the issue by scrolling with our finger in the bottom right of the screen.

 # Wi-Fi problems
We noticed it was hard to keep track of what Wi-Fi the device was connected to so we added a Wi-Fi credentials tab to keep track of it easily.

 # Memory problems
When connecting the trafiklab API to the device we noticed that it crashed due to the amount of stops there was, to fix it we stored the stops in Karlskrona to a file that the device then uses to get all the needed stops.
