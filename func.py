from cryptography.fernet import Fernet
from selenium.webdriver.chrome.options import Options
import os
import sys
import time

#region general_functions

def remove(string, removestr):
  return string.replace(removestr, "")

def convert_seconds(seconds):
  seconds = seconds % (24 * 3600)
  hour = seconds // 3600
  seconds %= 3600
  minutes = seconds // 60
  seconds %= 60
     
  return (str(hour) + "hr " + str(minutes) + "min " + str(seconds) + "s")

#endregion

#region logs

def update_log(new_log):
  with open('data/log.txt', 'a') as log:
    log.write(new_log + '\n')

#endregion

#region settings

def get_dev_mode():
  if input("Would you like to run the program in developer mode? (y/n): ").lower().strip() == 'y':
    print("Developer mode enabled.\n")
    return True
  return False

#endregion

#region credentials

def encrypt_credentials(username, password):
  key = Fernet.generate_key()
  cipher_suite = Fernet(key)
  ciphered_text = cipher_suite.encrypt(bytes(username + '\n' + password, 'utf-8'))
  with open('data/key.key', 'wb') as f:
    f.write(key)
  return ciphered_text

def get_decrypted_credentials_in_file():
  with open('data/credentials.bin', 'rb') as f:
    ciphered_text = f.read()
  with open('data/key.key', 'rb') as f:
    key = f.read()

  cipher_suite = Fernet(key)
  plain_text = cipher_suite.decrypt(ciphered_text)
  username, password = plain_text.decode('utf-8').split('\n')
  return username, password

def change_credentials():
  if os.path.exists('data/credentials.bin'):
    os.remove('data/credentials.bin')
  if os.path.exists('data/key.key'):
    os.remove('data/key.key')
  print("Credentials cleared.\n")
  return get_credentials()

def get_credentials():
  if os.path.exists('data/credentials.bin') and os.path.exists('data/key.key'):
    if input("Would you like to change any credentials? (y/n): ").lower().strip() == 'y':
      if os.path.exists('data/credentials.bin'):
        os.remove('data/credentials.bin')
      if os.path.exists('data/key.key'):
        os.remove('data/key.key')

  if not os.path.exists('data/credentials.bin') and not os.path.exists('data/key.key'):
    print("Please enter your credentials.")
    username = input("Username: ")
    password = input("Password: ")
    print("Clearing screen.\n")
    time.sleep(1)
    print("\033c")
    with open('data/credentials.bin', 'wb') as f:
      f.write(encrypt_credentials(username, password))
    print("Credentials saved.\n")

  else:
    print("Credentials found. Getting credentials from file.\n")

  return get_decrypted_credentials_in_file()

#endregion

#region story_id

def get_story_id():
  if not os.path.exists('data/story_id.txt'):
    with open('data/story_id.txt', 'w') as f:
      f.write('15')

  with open('data/story_id.txt', 'r') as f:
    story_id = f.read()

  if input("Would you like to change the story id? Your current story id is " + story_id + ". (y/n): ").lower().strip() == 'y':
    story_id = input("Please enter the new story id: ")
    update_story_id(story_id)
    print("Story ID saved.\n")

  return story_id

def update_story_id(current_story_id):
  new_story_id = str(int(current_story_id) + 1)
  with open('data/story_id.txt', 'w') as f:
    f.write(new_story_id)
  return new_story_id

#endregion

#region chrome_options

def get_chrome_options(devmode):
  chrome_options = Options()
  chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
  chrome_options.add_argument('--log-level=3')
  chrome_options.add_argument("--start-maximized")
  chrome_options.add_argument("--disable-extensions")
  return chrome_options

#endregion

#region login

def login(driver, username, password, showmessage=True):
  if showmessage:
    print("\nAttempting to login...")

  driver.get('https://www.zbschools.sg')

  login_popup_button = driver.find_element('id', 'ulogin')
  login_popup_button.click()

  username_field = driver.find_element('id', 'inputLoginId')
  username_field.send_keys(username)

  password_field = driver.find_element('id', 'inputPassword')
  password_field.send_keys(password)

  submit_button = driver.find_element('id', 'btn_submit')
  submit_button.click()

  if driver.current_url == 'https://www.zbschools.sg/cos/o.x?c=/ca7_zbs/zbsauth':
    print("Login failed! Please check your username and password, which will be shown below:")
    time.sleep(1)
    print("\nUsername: " + username)
    print("Password: " + password)
    if input("Would you like to change your credentials? (y/n): ").lower().strip() == 'y':
      change_credentials()
      print("Please restart the program for changes to take effect.")
      time.sleep(1)
      sys.exit()
    else:
      print("Exiting program.")
      time.sleep(1)
      sys.exit()
  
  else:
    if showmessage:
      print("Login successful!\n")

#endregion
