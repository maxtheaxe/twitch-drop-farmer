# account-creator.py - twitch-drop-farmer - maxtheaxe
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
from win10toast import ToastNotifier

# set path to chrome driver for packaging purposes
# ref: https://stackoverflow.com/questions/41030257/is-there-a-way-to-bundle-a-binary-file-such-as-chromedriver-with-a-single-file
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))

# launch() - launch sequence to get driver started, logged in, and prepared to work
def launch(username, password, headless = False, verbose = False, proxy = None):
	# print("\tLaunching a bot...\n")
	driver = start_driver(headless, proxy) # start the driver and store it (will be returned)
	proxy_auth(driver) # make sure everything looks okay for bot
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
	# add ublock origin to reduce impact, block stuff
	options.add_extension("ublock_origin.crx")
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

# create_twitch() - make new twitch account
def create_twitch(driver, username, password, email_domain = "flarn.xyz"):
	# first, navigate to the signup page
	driver.get("https://www.twitch.tv/signup")
	# wait until page is properly loaded
	try: # wait (for 10 sec) and make sure
		wait = WebDriverWait(driver, 10)
		# wait until terms of service link is clickable
		element = wait.until(EC.element_to_be_clickable(
			(By.xpath, "//a[@href='https://www.twitch.tv/p/legal/terms-of-service/'")))
		# if it is visible, it's loaded properly
		if EC.visibility_of(driver.find_element_by_xpath(
			"//a[@href='https://www.twitch.tv/p/legal/terms-of-service/'")):
			if verbose:
				print("\tSuccessfully loaded signup page.\n")
	except: # something went wrong, we weren't able to load the page properly
		print("\tError: Page not loading.\n")
		sys.exit()
	# next, type in your details
	driver.find_element_by_id("signup-username").send_keys(username) # send username
	driver.find_element_by_id("password-input").send_keys(password) # send password
	driver.find_element_by_id("password-input-confirmation").send_keys(password) # verify
	# now enter a birth month
	bday_dropdown = driver.find_element_by_xpath(
		"//select[@data-a-target='birthday-month-select']") # find the dropdown
	bday_dropdown.click() # click the dropdown
	bday_dropdown.send_keys(Keys.DOWN) # press the down arrow to select january
	bday_dropdown.send_keys(Keys.RETURN) # press enter to save that
	# now enter a day of the month
	bday_day = driver.find_element_by_xpath(
		"//input[@aria-label='Enter the day of your birth']") # find the element
	bday_day.send_keys("1") # enter the number
	# now enter the year
	bday_year = driver.find_element_by_xpath(
		"//input[@aria-label='Enter the year of your birth']") # find the element
	bday_year.send_keys("1985") # type it in
	# now enter the email
	email = username + email_domain # build the email
	driver.find_element_by_id("email-input").send_keys(email) # type in the email
	# now click the signup button
	signup_button = driver.find_element_by_xpath("//div[@class='tw-flex-grow-0']") # find it
	signup_button.click() # click it
	# now check if a captcha has appeared
	captcha_check(driver) # call checker
	return

# captcha_check() - checks to see if a captcha page is there; calls user if so
# reference: https://towardsdatascience.com/how-to-make-windows-10-toast-notifications-with-python-fb3c27ae45b9
def captcha_check(driver, first = True):
	# account for possible loading time (can't wait for an indicator
	# to appear because that's the point--we wanna see if it does)
	try: # see if arkose labs link is somewhere on the page
		driver.find_element_by_xpath("//a[@aria-label='Open Arkose Labs website']")
		# now alert the user that there is, in fact, a captcha for them to complete
		toaster = ToastNotifier()
		toaster.show_toast("Twitch Account Creator","Help me with this captcha, please!")
		input("Hit Enter to continue...") # wait for user prompt to resume
	except: # wait and try again, calling self indicating second time
		if (first == True): # if first call
			time.sleep(10) # wait 10 seconds
			captcha_check(driver, False) # call self again
	return # if we've gotten here, there's no captcha--it's safe to move on

# grab_creds() - grabs credentials from file
def grab_creds():
	# read in data and add it to 2d array data
	data = list(csv.reader(open("new-account-combos.csv")))
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

# get_driver_info() - export driver info in case restart is desired
# reference: https://stackoverflow.com/questions/8344776/can-selenium-interact-with-an-existing-browser-session
def get_driver_info(driver):
	url = driver.command_executor._url       # "http://127.0.0.1:60622/hub"
	session_id = driver.session_id            # '4e167f26-dc1d-4f51-a207-f761eaf73c31'
	return [url, session_id] # return both things in a list

# save_drivers() - gets and saves driver info for every driver
def save_drivers(driver_list):
	# make new list to store info
	saved_info = []
	# loop over all drivers
	for i in range(len(driver_list)):
		# append info for each driver to main list as sublist
		save_info.append(get_driver_info(driver_list[i]))
	# return all saved info as 2d list
	return saved_info

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
	num_bots = 15
	headless = False
	verbose = False
	proxy = read_proxies("proxy-list.txt") # read in proxies from file (new one on every line)
	bot_list = cavalry(num_bots, headless, verbose, proxy) # store the bots in a list for easy closing later
	# Tell Python to run the handler() function when SIGINT is recieved
	signal.signal(signal.SIGINT, signal_handler)
	print("\tUse Control + C to close all bots.") # print instructions
	# wait 25 min for login code
	time.sleep(1500)
	while True:
		# run maintenance every 20 minutes
		try:
			group_maintenance(bot_list)
		time.sleep(1200)
		# ask for a stream link
		# selected_stream = input("\tPaste a stream link and hit enter.\n")
		# tell all the bots to enter that stream
		# enter_stream(selected_stream)
		pass