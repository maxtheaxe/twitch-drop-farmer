# Twitch Drop Farmer
* Idle as many accounts you want
* Periodic maintenance (switches to new streams, handles errors)
* Supports proxies

## Motivations
* Frustration regarding my lack of Valorant drops
* Curiosity about viability (i.e. can Twitch block bots like these)
* Quarantine boredom

## Technologies
* Python 3.X
* Selenium
* win10toast
* A few more basics

## Installation
_For now, I'm not gonna build executables to minimize abuse_
* Clone the repository to a local directory
* Install the dependencies
* [Download appropriate chromedriver](https://sites.google.com/a/chromium.org/chromedriver/home) and place in same directory
* Create `account-combos.csv` (username, password)
* Optional: Create `proxy-list.txt` (one proxy per line)
* Optional: Create `proxy-auth.txt` (username \n password)

## Usage
* Run `farmer.py`
* Type in desired number of accounts, press Enter
* Enter account verification codes when prompted

## Disclaimers & Notes
* Primarily: be considerate⁠—save keys for the rest of us (I waited to release this to minimize abuse)
* Not super practical for dedicated use⁠—this is a fun project
* Could _definitely_ be cleaned up, open to pull requests
* System resource usage is heavy
