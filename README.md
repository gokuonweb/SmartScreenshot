This script captures screenshots whenever a significant change in the screen 
is detected, based on a specified threshold.

Input:

    Directory: The folder where screenshots will be saved.
    Image Type: Choose between JPG or PNG formats.
    Image Prefix: A prefix for naming saved images (e.g., "screenshot").
    Threshold Change: A numeric value (typically between 20-30) that 
                      determines the sensitivity of change detection.

Output:

    Screenshots saved in the specified directory.

Usage:

    The script runs in the background, allowing you to capture screenshots 
    while watching videos for note-taking or other purposes.
    
    Key Controls:
        Press 'p' to pause screenshot capture.
        Press 'r' to resume screenshot capture.
        Press 'm' to manually take a screenshot, regardless of the threshold.
