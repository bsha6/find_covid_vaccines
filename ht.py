import time
import smtplib

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

def send_email(subject, message, toaddrs):
    fromaddr = 'FROM EMAIL HERE'

    # Setup the email server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # Add my account login name and password,
    server.login(fromaddr, "PASSWORD")
    
    # Create email message
    msg = 'Subject: {}\n\n{}'.format(subject, message)
    
    # Print the email's contents
    print('From: ', fromaddr)
    print('To: ', str(toaddrs))
    print('Message: ', msg)
    
    # Send the email
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

# Harris Teeter
def check_ht(url, xpaths, zip_code, toaddrs):
    """Determine Vaccine Availabilites at HT locations by zip code"""
    path = '/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(path)   # Run with display
    
    # Change cdp to look less like a bot
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source":
        "const newProto = navigator.__proto__;"
        "delete newProto.webdriver;"
        "navigator.__proto__ = newProto;"
    })
    driver.get(url)
    driver.delete_all_cookies()
    time.sleep(2.5)
#     driver.refresh()
    driver.implicitly_wait(10)
    
    # Get past eligibility screening questions
    try:
        time.sleep(4)
        screen = driver.find_element_by_xpath(xpaths[0]).click()
        screen2 = driver.find_element_by_xpath(xpaths[1]).click()
        time.sleep(1)
        state = driver.find_element_by_xpath(xpaths[2]).click()
        time.sleep(1)
        select_state = driver.find_element_by_xpath(xpaths[9]).click()
        time.sleep(0.5)
        screen3 = driver.find_element_by_xpath(xpaths[3]).click()
        time.sleep(1)
        screen4 = driver.find_element_by_xpath(xpaths[4]).click()
        time.sleep(0.5)

        dob = driver.find_element_by_xpath(xpaths[5])
        time.sleep(1)
        dob.send_keys('10/10/1955')
        time.sleep(1)
        submit = driver.find_element_by_xpath(xpaths[6]).click()
        time.sleep(2)
        schedule = driver.find_element_by_xpath(xpaths[7]).click()
        time.sleep(4)
    
        # Find appointment by zip code
        # ISSUES with captcha/detecting bot
        find_appt = driver.find_element_by_xpath(xpaths[10])
        find_appt.send_keys(zip_code)
        time.sleep(0.5)
        find = driver.find_element_by_xpath(xpaths[8]).click()
        time.sleep(4)
        response = driver.page_source
        time.sleep(5)
        
        # Extract HT availabilities from response
        soup = BeautifulSoup(response, 'lxml')
        warning_tags = soup.find_all(class_ = "kds-Text--s kds-Message-content")
        warning_msg = [tag.get_text() for tag in warning_tags]
        no_avail_check = 'None of the locations in your search currently have appointments available'
        
        text_positive = 'kds-Text--m text-positive-700'
        tags = soup.find_all(class_ = text_positive)
        avail_msg = [tag.get_text() for tag in tags]
        
        # Check for available appointments
        avail_check = 'Available Appointments for'
        if any(avail_check in msg for msg in avail_msg):
            print(avail_msg)
            
            # Create email message
            subject =  f"HT has Vaccines Available in {zip_code}"
            message = f"""\

            {avail_msg}
            
            Sign up for Appointments here: {url}

            This message is sent from a Python program."""

            send_email(subject, message, toaddrs)
        
        elif any(no_avail_check in msg for msg in warning_msg):
            print("No appts available for zipcode:", zip_code)
            print(warning_msg)
        else:
            print('Not finding class tag for warning msg or tag for available appts')

    except NoSuchElementException:
        print('No such element exception')
    except NoSuchWindowException:
        print("No such window exception. HT may have used pop up asking if you're a robot.")
    finally:
        driver.quit()
    
xpaths = [
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li/div/div[2]/div[2]/div/div/div/button[1]',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[3]/div/div[2]/div[2]/div/div/div/button[2]',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[5]/div/div[2]/div[2]/div/div/div/select',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[6]/div/div[2]/div[2]/div/div/div/button[2]',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[8]/div/div[2]/div[2]/div/div/div/button[2]',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[10]/div/div[2]/div[2]/div/div/div/div/form/div[1]/input',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[10]/div/div[2]/div[2]/div/div/div/div/form/div[2]/button',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[11]/div/div[2]/div[2]/div/div/div/button',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div[2]/div[3]/div[1]/div/div/div/div[2]/form/button',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div/div/div/div/div/div/div/div/ul/li[5]/div/div[2]/div[2]/div/div/div/select/option[48]',
    '/html/body/div[1]/div/div[3]/div/main/div/section[2]/div/div/div[2]/div[3]/div[1]/div/div/div/div[2]/form/div/div[1]/div/input'
]

ht_url = 'https://www.harristeeterpharmacy.com/rx/covid-vaccine'
zip_code = 'ZIP CODE'
toaddrs = ['RECIPIENT EMAIL HERE']
check_ht(ht_url, xpaths, zip_code, toaddrs)
