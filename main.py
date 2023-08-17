import os
try:
  from selenium import webdriver
  from pypinyin import pinyin
except:
  os.system("python3 -m pip install selenium pypinyin")
  from selenium import webdriver
  from pypinyin import pinyin
from constants import *
from func import *
import atexit
import time

update_log("\n--- SESSION STARTED ---")
update_log("DateTime: " + time.strftime("%H:%M:%S", time.localtime()) + ", " + time.strftime("%d/%m/%Y", time.localtime()) + "\n")
session_start_time = time.time()

print(big_text)
print("Copyright 2023. All rights reserved. (c) ZK\n")

if not os.path.exists('data'):
  os.makedirs('data')

devmode = get_dev_mode()
username, password = get_credentials()
story_id = get_story_id()

print("\nTo exit, press Ctrl + C")
time.sleep(1)
print("You can continue doing other things while this program is running")
time.sleep(1)
print("Do not close the browser window that opens, or login to ZBSchools from somewhere else.")
time.sleep(1)
print("If there is an error, increase the story ID by 1 and try again.")
time.sleep(1)

driver = webdriver.Chrome(options=get_chrome_options(devmode))
driver.maximize_window()
driver.get("https://www.zbschools.sg/")

login(driver, username, password)

quizzes_per_min = []
points_per_min = []
quizzes_completed_this_session = 0

def on_exit():
  if len(quizzes_per_min) == 0 or len(points_per_min) == 0 or quizzes_completed_this_session == 0:
    update_log("--- SESSION ENDED ---\n")
    return sys.exit(1)

  update_log(f"\nSession Duration: {convert_seconds(round(time.time() - session_start_time))}")
  update_log(f"Average Quizzes Per Minute: {round(sum(quizzes_per_min) / len(quizzes_per_min), 2)}")
  update_log(f"Average Points Per Minute: {round(sum(points_per_min) / len(points_per_min), 2)}")
  update_log(f"Total Quizzes Completed: {quizzes_completed_this_session}")
  update_log("--- SESSION ENDED ---\n")

  print("\033c--- SESSION ENDED ---"); time.sleep(1)
  print(f"Session Duration: {convert_seconds(round(time.time() - session_start_time))}"); time.sleep(1)
  print(f"Average Quizzes Per Minute: {round(sum(quizzes_per_min) / len(quizzes_per_min), 2)}"); time.sleep(1)
  print(f"Average Points Per Minute: {round(sum(points_per_min) / len(points_per_min), 2)}"); time.sleep(1)
  print(f"Total Quizzes Completed: {quizzes_completed_this_session}")

  driver.quit()

  time.sleep(5)
  return sys.exit(1)

atexit.register(on_exit)

while True:
  driver.get(base_story_url + str(story_id))

  start_time_for_this_quiz = time.time()

  print("\nStory ID: " + str(story_id))

  if driver.current_url == "https://www.zbschools.sg/":
    print("Story does not exist. Skipping...")
    update_log(f"Story ID: {story_id} | Story does not exist. Skipping...")
    story_id = update_story_id(story_id)
    continue

  try:
    start_quiz_button = driver.find_element('xpath', '//*[@id="lo_main"]/div/div[3]/div/div[1]/div[1]/div[3]/div/div/a[4]')
  except:
    print("Story does not have a quiz. Skipping...")
    update_log(f"Story ID: {story_id} | Story does not have a quiz. Skipping...")
    story_id = update_story_id(story_id)
    continue

  element = driver.find_element("xpath", "/html/body/div/div/div/div/div/div[2]/div[3]/div")
  driver.execute_script("""
  var element = arguments[0];
  element.parentNode.removeChild(element);
  """, element)

  passage = remove(driver.find_element('xpath', "html/body/div/div/div/div/div/div[3]/div/div[1]/div[1]/div[6]").text, '"')
  start_quiz_button.click()

  time.sleep(1) # wait for quiz to load
  driver.switch_to.frame('litebox_iframe')

  error_message = "None"

  amount_of_questions_in_this_quiz = len(driver.find_elements('xpath', "/html/body/div/div/form/div")) - 1
  amount_of_questions_done = 0

  for i in range(1, amount_of_questions_in_this_quiz + 1):
    print("\nStory ID: " + str(story_id) + " | Question " + str(i))
    
    answer = ""

    try:
      question = driver.find_element('xpath', "/html/body/div/div/form/div[" + str(i) + "]/div[1]/div[1]/h3/span").text
    except:
      print("Story ID: " + str(story_id) + " | Question " + str(i) + " | Question not found. Skipping...")
      continue

    if "_" in question: # qntype 1
      try:
        parts = question.split("_")
        part1 = passage.find(parts[0])
        part2 = passage.find((parts[len(parts) - 1]))
        r = range((part2 - part1) - len(parts[0]))

        for n in r:
          answer += passage[n + part1 + len(parts[0])]
      except:
        print("Story ID: " + str(story_id) + " | Question " + str(i) + " | Error finding answer. Skipping...")
        continue

    else: # qntype 0
      try:
        exact_question = driver.find_element('xpath', "/html/body/div/div/form/div[" + str(i) + "]/div[1]/div[1]/h3/span/b/u").text
        answer = pinyin(exact_question)
        answer = ' '.join([x[0] for x in answer])
      except:
        print("Story ID: " + str(story_id) + " | Question " + str(i) + " | Error finding answer. Skipping...")
        continue

    amount_of_options = len(driver.find_elements('xpath', f"/html/body/div/div/form/div[{i}]/div[2]/table/tbody/tr"))

    try:
      for a in range(1, amount_of_options + 1):
        if driver.find_element('xpath', f"/html/body/div/div/form/div[{i}]/div[2]/table/tbody/tr[{a}]/td[2]").text == answer:
          driver.find_element('xpath', f"/html/body/div/div/form/div[{i}]/div[2]/table/tbody/tr[{a}]/td[1]/input").click()
          break
    except Exception as e:
      print("Story ID: " + str(story_id) + " | Question " + str(i) + " | Error selecting answer. Skipping...")
      error_message = str(e)
      continue
    
    print("Story ID: " + str(story_id) + " | Question " + str(i) + " | Question Completed")
    amount_of_questions_done += 1

  try:
    submit_button = driver.find_element('xpath', f"/html/body/div/div/form/div[{amount_of_questions_in_this_quiz + 1}]/input")
    submit_button.click()
  except:
    print("Story ID: " + str(story_id) + " | Submit Button Not Found. Skipping...")
    update_log(f"Story ID: {story_id} | Submit Button Not Found. Skipping...")
    story_id = update_story_id(story_id)
    continue

  time.sleep(0.05)
  
  try:
    score = driver.find_element('xpath', '//*[@id="quiz_questions_container"]/div[1]/div[2]/span').text
  except:
    score = "Error Finding Score"
  print("\nStory ID: " + str(story_id) + " | Score: " + score)

  end_time_for_this_quiz = time.time()

  if devmode:
    print("Story ID: " + str(story_id) + " | Time Taken (Raw): " + str(round(end_time_for_this_quiz - start_time_for_this_quiz, 2)) + " seconds | Time Taken (No Wait): " + str(round(end_time_for_this_quiz - start_time_for_this_quiz - (amount_of_questions_done * 0.05) - 1.05, 2)) + " seconds")

  quizzes_per_min.append(round(60 / (end_time_for_this_quiz - start_time_for_this_quiz), 2))
  print("\nAverage Quizzes Per Minute: " + str(round(sum(quizzes_per_min) / len(quizzes_per_min), 2)))

  points_per_min.append(round(60 / (end_time_for_this_quiz - start_time_for_this_quiz) * 150, 2))
  print("Average Points Per Minute: " + str(round(sum(points_per_min) / len(points_per_min), 2)))

  update_log(f"Story ID: {story_id} | Questions Done: {amount_of_questions_done} | Questions Allocated: {amount_of_questions_in_this_quiz} | Score: {score} | Raw Time Taken: {str(round(end_time_for_this_quiz - start_time_for_this_quiz, 2))} seconds | Errors: {error_message}")
  print("\nStory ID: " + str(story_id) + " | Quiz Completed, Log Updated")

  story_id = update_story_id(story_id)
  quizzes_completed_this_session += 1
