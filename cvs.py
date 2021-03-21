import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import smtplib

def parse_tag_list(tag_list):
    """Parse list of html tags"""
    text_list = []
    for row in tag_list:
        text = row.get_text().split(', ')
        if len(text) > 2:
            print("Warning! Length of text split is: ", len(text))
            print("Comma in city name: ", text)
        text_list.append(text[0])
    return text_list

def check_status(df, cities_list):
    """Check if any cities in cities_list have availabilities"""
    df_nearby = df.loc[df['cities'].isin(cities_list)]
    check = df_nearby.loc[df_nearby['status'] == 'Available']
    if check.empty == True:
        print('Not available in any of these cities: ', cities_list)
    else:
        print('Vaccine is available here:')
        print(check)
    return check

def send_email(subject, message, toaddrs):
    fromaddr = 'FROM EMAIL HERE'

    # Setup the email server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # Add my account login name and password,
    server.login("EMAIL", "PASSWORD")
    
    # Create email message
    msg = 'Subject: {}\n\n{}'.format(subject, message)
    
    # Print the email's contents
    print('From: ', fromaddr)
    print('To: ', str(toaddrs))
    print('Message: ', msg)
    
    # Send the email
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

def check_cvs_then_email(url, xpath, city_list, to_address):
    """Determine Vaccine Availabilites at CVS locations and email results"""
    path = '/usr/local/bin/chromedriver'
    
    # Get VA availabilities and save html into response
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(path, options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    state = driver.find_element_by_xpath(xpath).click()
    response = driver.page_source
    driver.quit()
    
    # Extract availability table from response
    soup = BeautifulSoup(response, 'lxml')
    cities_tags = soup.select("[class~=city]")
    status_tags = soup.select("[class~=status]")
    
    cities = parse_tag_list(cities_tags)
    status = parse_tag_list(status_tags)
    d = {'cities': cities, 'status': status}
    df_cvs = pd.DataFrame(d)
    
    # Check all cities in State
    check_all = check_status(df_cvs, df_cvs.cities.values)
    # Check close cities
    check_city_list = check_status(df_cvs, city_list)
    
    # If vac available, send email
    if check_city_list.empty == True:
        pass
    else:
        print('Available')

        # Create email message
        subject =  f"Vaccines Available in {check_city_list['cities'].tolist()}"
        message = f"""\
        Vaccines are available:
        {check_city_list}

        Sign up for Appointments here: {url}

        This message is sent from a Python program."""

        send_email(subject, message, to_address)
        
# CVS Variables
url = 'https://www.cvs.com/immunizations/covid-19-vaccine'
va_xpath_full = '/html/body/content/div/div/div/div[3]/div/div/div[2]/div/div[5]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div[2]/ul/li[19]/div/a/span'
va_close_cities = ['LIST', 'OF', 'CITIES', 'HERE']

# Check for vaccines and email results
toaddrs = ['RECIPIENT EMAIL ADDRESS HERE']
check_cvs_then_email(url, va_xpath_full, va_close_cities, toaddrs)
