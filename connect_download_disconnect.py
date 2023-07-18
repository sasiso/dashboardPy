import subprocess
import pyautogui
from pywinauto import Desktop, findwindows
from pywinauto import Application
import time
# Launch the process
app = Application(backend='uia').start("C:\\SiLabs\\MCU\\Utilities\\FLASH Programming\\Static Programmers\\Windows Console\\FlashUtil.exe")


# Wait for the application to load
# Add appropriate delays if needed to ensure the application is ready

# Find the main window of the application
main_window = app.window(title="Silicon Laboratories Flash Utility")
# Find the checkbox control
checkbox = main_window.child_window(title="Disable Dialogs on Connect and Disconnect", control_type="CheckBox")

# Check the checkbox
if not checkbox.get_toggle_state():
    checkbox.click()

# Find the button based on its text
button = main_window.child_window(title="Connect", control_type="Button")
time.sleep(.1)
# Click the button
button.click()

time.sleep(.1)
# Find the pop-up window
#popup_window = app.window(title="FlashUtil")

# Click the button on the pop-up window
#popup_window.child_window(title="OK", control_type="Button").click()

tab_control = main_window.TabControl

# Select the desired tab
tab_control.select("Download Hex File/Go/Stop")
time.sleep(.1)
checkbox = main_window.child_window(title="Disable Dialogs on Download", control_type="CheckBox")
# Check the checkbox
if not checkbox.get_toggle_state():
    checkbox.click()

time.sleep(1)
# Find the button based on its text
button = main_window.child_window(title="Download", control_type="Button")
time.sleep(.1)

# Find the input box control
input_box = main_window.child_window(control_type="Edit", found_index=0)  # Assuming it is an Edit control

# Get the text from the input box
input_box.set_text('C:\\Users\\sss\\Desktop\\Archive\\multi-use-reader-firmware\\workspace\project\\Debug\\project.hex')

# Copy the text to clipboard
#app.clipboard.set_text(text)

# Click the button
button.click()

time.sleep(5)

# Select the desired tab
tab_control.select("Connect/Disconnect")
button = main_window.child_window(title="Disconnect", control_type="Button").click()
main_window.close()
