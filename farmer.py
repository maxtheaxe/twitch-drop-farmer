# farmer.py - twitch-drop-farmer - maxtheaxe
# I just wanna know if it's really this easy
# code taken in part from my client built for zoom.rip
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
# from bs4 import BeautifulSoup as bs
import sys
import re
import time
import random
import signal
import os
import inspect
from fake_useragent import UserAgent
import csv

# set path to chrome driver for packaging purposes
# ref: https://stackoverflow.com/questions/41030257/is-there-a-way-to-bundle-a-binary-file-such-as-chromedriver-with-a-single-file
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))

# launch() - launch sequence to get driver started, logged in, and prepared to work
def launch(username, password, headless = False, verbose = False, proxy = None):
	# print("\tLaunching a bot...\n")
	driver = start_driver(headless, proxy) # start the driver and store it (will be returned)
	proxy_auth(driver) # make sure everything looks okay for bot
	driver.get("https://www.twitch.tv/fl0m") # open first stream
	change_settings(driver) # make it use as little resources as possible
	login(driver, username, password, verbose) # log into the room with the room link and name
	# print("\t", bot_name, "successfully launched.\n")
	return driver # return driver so it can be stored and used later

# start_driver() - starts the webdriver and returns it
# reference: https://tarunlalwani.com/post/selenium-change-user-agent-different-browsers/
# reference: https://groups.google.com/forum/?hl=en-GB#!topic/selenium-users/ZANuzTA2VYQ
# reference: https://stackoverflow.com/questions/11450158/how-do-i-set-proxy-for-chrome-in-python-webdriver
# reference: https://stackoverflow.com/questions/48454949/how-do-i-create-a-random-user-agent-in-python-selenium
def start_driver(headless = False, proxy = None):
	# set path to chrome driver for packaging purposes
	chromedriver = os.path.join(current_folder,"chromedriver.exe")
	# geckodriver = os.path.join(current_folder,"geckodriver.exe") # ff
	# setup webdriver settings
	options = webdriver.ChromeOptions()
	# options = webdriver.FirefoxOptions() # ff
	# profile = webdriver.FirefoxProfile() # ff
	# add auto auth for proxies
	options.add_extension("Proxy Auto Auth.crx")
	# other settings
	options.headless = headless # headless or not, passed as arg
	options.add_experimental_option('excludeSwitches', ['enable-logging']) # chrome only maybe
	# make window size bigger
	# options.add_argument("--window-size=1600,1200")
	# add proxy if one is given
	if (proxy != None):
		 # IP:PORT or HOST:PORT
		options.add_argument('--proxy-server=%s' % proxy)
		print("using a proxy: ", proxy)
		# profile.set_preference("network.proxy.type", 1) # ff
		# profile.set_preference("network.proxy.http", proxy) # ff
		# profile.set_preference("network.proxy.http_port", port) # ff
	# add a fake user agent
	# user_agent = UserAgent().random # generate random useragent
	# print("user agent: ", user_agent) # check what it is
	# options.add_argument(f'user-agent={user_agent}')
	# profile.set_preference("general.useragent.override", user_agent) # ff
	# update profile (ff)
	# profile.update_preferences() # ff
	# start webdriver and return it
	# return webdriver.Firefox(firefox_profile = profile, options = options, executable_path = geckodriver)
	return webdriver.Chrome(options = options, executable_path = chromedriver)

# proxy_auth() - auth proxy at start
# reference: https://stackoverflow.com/questions/46330245/userpass-proxies-with-selenium
def proxy_auth(driver):
	# open proxy credentials file in read mode
	with open("proxy-auth.txt", 'r') as file_handle:
		# read file content into list (each detail is on a line)
		auth = file_handle.readlines()
	# navigate to extension settings
	driver.get("chrome-extension://ggmdpepbjljkkkdaklfihhngmmgmpggp/options.html")
	# type in details
	driver.find_element_by_id("login").send_keys(auth[0]) # username
	driver.find_element_by_id("password").send_keys(auth[1]) # password
	driver.find_element_by_id("retry").clear()
	driver.find_element_by_id("retry").send_keys("2") # retry times
	# save it
	driver.find_element_by_id("save").click()
	# check it
	driver.get("https://www.whatsmyip.org/") # navigate to helpful website
	# stop for a sec so I can see
	time.sleep(1)
	return # move on

# login() - logs into the twitch acc
# reference: https://crossbrowsertesting.com/blog/test-automation/automate-login-with-selenium/
# reference: https://stackoverflow.com/questions/19035186/how-to-select-element-using-xpath-syntax-on-selenium-for-python
# future: add password support (for locked rooms)
def login(driver, username, password, verbose = False):
	# print("\tLogging in...\n")
	web_link = "https://www.twitch.tv/login" # twitch login page
	try: # try opening the given link, logging in
		driver.get(web_link) # open zoom meeting login page
		driver.find_element_by_id('login-username').send_keys(username) # enter username
		# enter password
		driver.find_element_by_id('password-input').send_keys(password)
		# find and click login button
		driver.find_element_by_xpath(
			"//div[@class='tw-mg-t-2']//button[@data-a-target='passport-login-button']").click()
	except: # bad link, try again
		print("\tError: Login Failed.\n")
		sys.exit()
	try: # wait and make sure we're logged in, loaded into the room
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'facebook-connect-button')))
		if EC.visibility_of(driver.find_element_by_class_name("facebook-connect-button")):
			if verbose:
				print("\tSuccessfully logged in.\n")
	except: # something went wrong, we weren't able to load into the room
		print("\tError: Login Failed.\n")
		sys.exit()

# grab_creds() - grabs credentials from file
def grab_creds():
	# read in data and add it to 2d array data
	data = list(csv.reader(open("account-combos.csv")))
	# chop off the headers
	data = data[1:]
	return data

# read_proxies() - feed a list of proxies from a file
# ref: https://codippa.com/how-to-read-a-file-line-by-line-into-a-list-in-python/
def read_proxies(file_name):
	# open file in read mode
	with open(file_name, 'r') as file_handle:
		# read file content into list broken up by line
		lines = file_handle.readlines()
	return lines # return list of proxies

# cavalry() - brings the "cavalry," by launching bots with creds from list
def cavalry(num_bots = 1, headless = False, verbose = False, proxy = None):
	driver_list = [] # create list for storing newly-created bots
	creds = grab_creds() # store creds in 2d array
	for i in range(num_bots): # loop for as many times as num bots desired
		# set bot_name by popping name from attendance list (name_options)
		username = creds[i][0] # get username from first element on each sublist
		password = creds[i][1] # get password from second element on each sublist
		# launch another driver/client with the given info
		driver = launch(username, password, headless, verbose, proxy[i])
		# store the newly-created bot in our list of drivers
		driver_list.append(driver)
	return driver_list # return the list of newly-created drivers

# enter_stream() - enters a given stream on all the bots
def enter_stream(stream_link):
	global bot_list # bring in the bot list
	# for all bots stored in master list
	for i in range(len(bot_list)):
		bot_list[i].get(stream_link) # navigate to the stream
	return

# change_settings() - change settings for max performance
def change_settings(driver):
	# hover over video player
	video_player = driver.find_element_by_class_name('video-player__default-player')
	# build new action chain to do so
	action = ActionChains(driver)
	# hover over own name on participants list
	action.move_to_element(video_player).perform()
	# find the gear cog and click
	# gear = driver.find_element_by_id('7f0643a6c83f8d0cdefcea447825c365').click()
	gear = driver.find_element_by_xpath(
		"//div[@data-test-selector='settings-menu-button__animate-wrapper']//button[@data-a-target='player-settings-button']")
	gear.click()
	# find quality dropdown and click
	dropdown = driver.find_element_by_xpath(
		"//div[contains(text(), 'Quality')]")
	dropdown.click()
	# find 160p quality setting and click
	driver.find_element_by_xpath(
		"//div[@data-a-target='player-settings-submenu-quality-option']//div[contains(text(), '160p')]").click()
	# next, make the window much smaller
	# driver.execute_script("window.resizeTo(516,300)")
	driver.set_window_size(516, 300)
	return

# signal_handler() - handles closing the program, to ensure all drivers are quit properly
# reference: https://www.devdungeon.com/content/python-catch-sigint-ctrl-c
def signal_handler(signal_received, frame):
	global bot_list # I've never used global variables with python, so idrk what I'm doin
	# Handle any cleanup here
	print("\n\tClosing all bots, please wait...\n")
	# for all bots stored in master list
	for i in range(len(bot_list)):
		bot_list[i].quit() # quit each bot window
	print("\tAll done! Hopefully you got some drops!\n")
	sys.exit(0)

def main(argv):
	print("\n\t--- zoom.rip | making remote learning fun ---\n")
	driver_list = [] # store the bots so we can close 'em later
	main_driver = launch("xxx", False)
	driver_list.append(main_driver) # store the main one in the list
	go_dark(driver[0])
	time.sleep(60)

if __name__ == '__main__':
	# main(sys.argv)
	num_bots = 1
	headless = False
	verbose = False
	proxy = read_proxies("proxy-list.txt") # read in proxies from file
	bot_list = cavalry(num_bots, headless, verbose, proxy) # store the bots in a list for easy closing later
	# Tell Python to run the handler() function when SIGINT is recieved
	signal.signal(signal.SIGINT, signal_handler)
	print("\tUse Control + C to close all bots.") # print instructions
	while True:
		# ask for a stream link
		selected_stream = input("\tPaste a stream link and hit enter.\n")
		# tell all the bots to enter that stream
		enter_stream(selected_stream)
		pass