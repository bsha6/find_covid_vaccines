#!/usr/bin/env python
# coding: utf-8

import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import smtplib

# Giant
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

def check_giant(url, zip_code, to_address):
    """Determine Vaccine Availabilites at Giant locations by zip code"""
    path = '/usr/local/bin/chromedriver'
    
    # Get Zip Code availabilities and save html into response
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(path, options=options)
    #driver = webdriver.Chrome(path)   # Run with display
    driver.get(url)
    
    #Check and get past queue it screen (new as of 3/22/21)
    driver.implicitly_wait(60)
    time.sleep(20)
    
    try:
        patient_advisory = driver.page_source
        time.sleep(1.5)
        soup_appts = BeautifulSoup(patient_advisory, 'lxml')
        appt_error_tags = soup_appts.find(class_= 'appointmentTypes')

        if not appt_error_tags:
            print('Giant: no appt error msg found')
        else:
            appt_error_txt = appt_error_tags.get_text()
            no_appts_avail = 'There are currently no COVID-19 vaccine appointments available'
    
            if no_appts_avail in appt_error_txt:
                print('No Giant appointments available in zip code:', zip_code)
                driver.quit()
                exit()            
            else:
                print('Found appt_error_tag, but appt_error_txt not found')
                print(appt_error_tag)
                driver.quit()
                exit()
    except Exception as e:
        print(e)
        
    # Search zip code and see if any appts available
    try:
        text_area = driver.find_element_by_id('zip-input')
        text_area.send_keys(zip_code)
        button = driver.find_element_by_id('btnGo').click()
        wait = WebDriverWait(driver, 1)
        response = driver.page_source
        driver.quit()

        # Extract availability table from response
        soup = BeautifulSoup(response, 'lxml')
        error = soup.find(id='ZipError').get_text()

        # Read error_msg and if no errors email that vaccines are available
        booked_error_msg = 'There are no locations with available appointments'
        zip_error_msg = 'ZIP code does not exist'
        if booked_error_msg in error:
           print('Giant:', error)
        elif zip_error_msg in error:
           print('Giant:', error)
        else:
           print("Giant has availabilites in zip code:", zip_code)
           # Create email message
           subject =  f"Vaccines Available in {zip_code}"
           message = f"""\

           Sign up for Appointments here: {url}

           This message is sent from a Python program."""

           send_email(subject, message, toaddrs)
    finally:
        driver.quit()

giant_url = 'https://giantfoodsched.rxtouch.com/rbssched/program/covid19/Patient/Advisory'
zip_code = 'ZIP CODE HERE'
toaddrs = ['RECEIPIENT EMAIL HERE']
check_giant(giant_url, zip_code, toaddrs)
