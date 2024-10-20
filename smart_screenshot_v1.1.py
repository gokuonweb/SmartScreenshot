import cv2
import numpy as np
import os
import pyautogui
import time
from pynput import keyboard
import functools
import re

paused = False  # To control pause and resume
manual_screenshot = False # to check for manual screenshot

def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print(f"\n[-] Keyboard interrupt occurred. Operation interrupted by user.")
            print('[>] If any bugs found or any feature request, please send a mail to gokuonweb@gmail.com. Thanks for using.')
            print('[!] Exiting after 60 seconds.')
            try:
                time.sleep(60)
                raise SystemExit()
            except KeyboardInterrupt:
                raise SystemExit()
        except Exception as e:
            print(f"[-] An error occurred in function '{func.__name__}' with description: {str(e)}")
            print('[>] If any bugs found or any feature request, please send a mail to gokuonweb@gmail.com. Thanks for using.')
            print('[!] Exiting after 120 seconds.')
            try:
                time.sleep(120)
                raise SystemExit()
            except KeyboardInterrupt:
                raise  SystemExit()
    return wrapper

@handle_exceptions
def history_count(dest_path):
    try:
        read_previous_count = os.path.join(dest_path, 'screenshot_count.ini')
        if os.path.exists(read_previous_count):
            with open(read_previous_count, 'r', encoding = 'utf-8') as read_file:
                previous_count = int(read_file.readline().strip())
            if previous_count != 0:
                print(f'\t[+] Last count of screenshot: {previous_count}. Continuing from that.')
                return previous_count
            else:
                return 0
        else:
            return 0
    except Exception as e:
        print('\t[-] Unable to locate last screenshot value.')
        return 0

@handle_exceptions
def get_user_inputs():
    # Get user input for destination folder, image type, and image name prefix
    input_level = [0,0,0,0]
    previous_count = 0
    destination_folder = ''
    image_type = ''
    image_name_start = ''
    percentage_threshold = ''
    while True:
        if input_level[0] == 0:
            try:
                destination_folder = input("[<] Enter the destination folder full path to save screenshots (can drag and drop the folder): ")
                destination_folder = destination_folder.replace('"','').replace("'","")
                if not os.path.exists(destination_folder):
                    print(f'\t[!] Path not found, directory created: {destination_folder}')
                    os.makedirs(destination_folder)
                else:
                    print(f'\t[+] Screenshots will be saved to: {destination_folder}')
                    previous_count = history_count(destination_folder)

                input_level[0]= 1
            except Exception as e:
                print('[-] Path does not exists or unable to create the path. Please try again.')
                continue

        if input_level[1] == 0:
            image_type = input("[<] Enter image type (jpg/png): ").lower()
            if image_type not in ["jpg", "png"]:
                print("[-] Invalid input! Please enter 'jpg' or 'png'.")
                continue
            else:
                input_level[1] = 1

        if input_level[2] == 0:
                image_name_start = None
                get_image_from_user = 0
                if previous_count != 0:
                    pattern = re.compile(r"^(.*)_\d+\.(jpg|png)$", re.IGNORECASE)
                    for filename in os.listdir(destination_folder):
                        if filename.lower().endswith(('.jpg', '.png')):
                            match = pattern.match(filename)
                            if match:
                                image_name_start = match.group(1)  # extracting the name
                                consent = input(f"[!] Previously used prefix detected: {image_name_start}, would you like to keep the same (y/n): ").strip().lower()
                                if consent == "n":
                                    get_image_from_user = 1
                                else:
                                    input_level[2] = 1
                                break
                    else: # else gets triggered only when for loop completes without finding any matching file
                        get_image_from_user = 1

                if get_image_from_user == 1:
                    image_name_start = input("[<] Enter the image name starting prefix (e.g.: screenshot): ")
                    if image_name_start.isalnum() or image_name_start.isascii():
                        input_level[2] = 1
                    else:
                        print('[-] Invalid image name prefix.')
                        continue

        if input_level[3] == 0 :
            percentage_threshold = input("[<] Enter the percentage change (e.g.: 10 or 20 or 30 etc.) threshold upon which screenshot will be taken: ")
            percentage_threshold = percentage_threshold.strip()
            try:
                percentage_threshold = int(percentage_threshold)
                input_level[3] = 1
            except ValueError:
                print("[-] Integer value required.")
                continue

        all_ones = all(x == 1 for x in input_level)
        if all_ones:
            break
        else:
            continue

    return destination_folder, image_type, image_name_start, percentage_threshold, previous_count

@handle_exceptions
def capture_screenshots(destination_folder, image_type, image_name_start, per_threshold, count_value):
    global paused, manual_screenshot
    last_frame = None
    screenshot_count = count_value
    print("Press 'P' to pause, 'R' to resume, and 'Ctrl+C' to stop.")
    seconds = 10
    for second in range(seconds, -1, -1):
        print(f'[!] Starting in {second} ...', end = '\r')
        time.sleep(1)
    print('[+] Started.                              ')
    paused = False
    while True:
        if paused:
            time.sleep(0.5)
            continue

        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Compare frames to detect changes
        if last_frame is None:
            last_frame = frame
        else:
            difference = cv2.absdiff(last_frame, frame)
            gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

            # Calculate the percentage of changed pixels
            changed_pixels = cv2.countNonZero(gray_diff)
            total_pixels = frame.shape[0] * frame.shape[1]
            change_percentage = (changed_pixels / total_pixels) * 100

            if change_percentage > per_threshold or manual_screenshot is True:
                manual_screenshot = False
                screenshot_count += 1
                save_screenshot(screenshot, destination_folder, image_type, image_name_start, screenshot_count)
                print(f"Change detected: {change_percentage:.2f}% of the image changed.")
                last_frame = frame

        time.sleep(1) # checking after every 1 second

@handle_exceptions
def save_screenshot(screenshot, destination_folder, image_type, image_name_start, screenshot_count):
    filename = f'{image_name_start}_{screenshot_count}.{image_type}'
    screenshot_path = os.path.join(destination_folder, filename)

    if image_type == "jpg":
        screenshot = screenshot.convert("RGB")

    screenshot.save(screenshot_path)
    print(f"Screenshot saved as {filename}")

    with open(os.path.join(destination_folder, 'screenshot_count.ini'), 'w', encoding = 'utf-8') as write_file:
        write_file.write(str(screenshot_count))

@handle_exceptions
def on_press(key):
    global paused, manual_screenshot

    try:
        if (key.char == 'p' or key.char == 'P') and paused is False:
            paused = True
            print("[!] Paused... Press 'R' to resume.")
        elif (key.char == 'r' or key.char == 'R') and paused is True:
            seconds = 3
            for second in range(seconds, -1, -1):
                print(f'[!] Resuming in {second} ...', end = '\r')
                time.sleep(1)

            print('[+] Resumed.                              ')
            paused = False

        elif key.char == 'm' or key.char == 'M':
            manual_screenshot = True

    except AttributeError:
        pass

@handle_exceptions
def main():
    destination_folder, image_type, image_name_start, per_threshold, sc_value = get_user_inputs()
    listener = keyboard.Listener(on_press = on_press)
    listener.start()
    capture_screenshots(destination_folder, image_type, image_name_start, per_threshold, sc_value)

if __name__ == "__main__":
    print('''
****************************************************************************
This script captures screenshots whenever a significant change in the screen 
is detected, based on a specified threshold. This runs in background.

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
        Press 'Ctrl + C' to exit the program
*****************************************************************************
    ''')
    main()


