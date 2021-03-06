# -*- coding: utf-8 -*-

import os
import re
import getpass
import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime, date

browser = webdriver.Chrome()

DESHE_CONNECTION_URL = "https://%s:%s@deshe.matrix.co.il/deshe/"
DATERANGE_REGEX = re.compile("(?P<from>\d{2}:\d{2}) - (?P<to>\d{2}:\d{2})")
HOUR_FORMAT = '%H:%M'

CONFIG_FILENAME = "config.txt"
CONFIG_LOGIN_SECTION = "Login"
CONFIG_USERNAME = "Username"
CONFIG_PASSWORD = "Password"
CONFIG_BASE64PASSWORD = "Base64password"
CONFIG_REPORT_SECTION = "ReportDetails"
CONFIG_REPORT_CUSTOMER_NAME = "CustomerName"
CONFIG_REPORT_PROJECT_NAME = "ProjectName"
CONFIG_REPORT_TASK_NAME = "TaskName"
CONFIG_REPORT_HALFHOUR = "HalfHour"
CONFIG_REPORT_DESCRIPTION = "Description"
CONFIG_REPORT_HALFHOUR_DESCRIPTION = "HalfHourDescription"

Config = ConfigParser.ConfigParser()

def choose_customer(customer_name):
    customer_name = customer_name.decode("cp1255")
    browser.execute_script("document.getElementById(\"ddlCustomers\").parentElement.querySelector('.ui-icon-triangle-1-s').click()")
    browser.execute_script("Array.prototype.slice.call(document.querySelectorAll(\".ui-menu-item\")).filter(function(v) { return v.innerText.indexOf('%s') > -1;})[0].click()" % customer_name)
    #customer = browser.find_element_by_name("ddlCustomers")
    #found = False
    #for option in customer.find_elements_by_tag_name('option'):
    #    if option.get_attribute("text") == customer_name:
    #        found = True
    #        break
    #if not found:
    #    raise Exception("Customer not found")

def choose_task(task_name):
    task_name = task_name.decode("cp1255")
    browser.execute_script("document.getElementById(\"ddlTasks\").parentElement.querySelector('.ui-icon-triangle-1-s').click()")
    browser.execute_script("Array.prototype.slice.call(document.querySelectorAll(\".ui-menu-item\")).filter(function(v) { return v.innerText.indexOf('%s') > -1;})[0].click()" % task_name)
    #task = browser.find_element_by_name("ddlTasks")
    #found = False
    #for option in task.find_elements_by_tag_name('option'):
    #    if option.text == task_name:
    #        option.click()
    #        found = True
    #        break
    #if not found:
    #    raise Exception("Task %s not found" % task_name)
        
def choose_project(project_name):
    project_name = project_name.decode("cp1255")
    browser.execute_script("document.getElementById(\"ddlProjects\").parentElement.querySelector('.ui-icon-triangle-1-s').click()")
    browser.execute_script("Array.prototype.slice.call(document.querySelectorAll(\".ui-menu-item\")).filter(function(v) { return v.innerText.indexOf('%s') > -1;})[0].click()" % project_name)
    #project = browser.find_element_by_name("ddlProjects")
    #found = False
    #for option in project.find_elements_by_tag_name('option'):
    #    if option.text == project_name:
    #        option.click()
    #        found = True
    #        break
    #if not found:
    #    raise Exception("Project %s not found" % project_name)
    
def fill_description(description):
    description = description.decode("cp1255")
    description_textarea = browser.find_element_by_name("txtElaboration")
    description_textarea.send_keys(description)

def select_day(day_to_select):
    # Calendar
    calendar = browser.find_element_by_id("generalCalendar")

    # Select day of the month
    for day in calendar.find_elements_by_class_name("calDay") + calendar.find_elements_by_class_name("calSelectedDay"):
        if day.text == str(day_to_select):
            day.click()
            break
            
def choose_time(from_time, to_time):
    from_hours = browser.find_element_by_id("txtFromHours")
    from_minutes = browser.find_element_by_id("txtFromMinutes")
    to_hours = browser.find_element_by_id("txtToHours")
    to_minutes = browser.find_element_by_id("txtToMinutes")
    from_hours.clear()
    from_hours.send_keys(from_time.split(":")[0])
    from_minutes.clear()
    from_minutes.send_keys(from_time.split(":")[1])
    to_hours.clear()
    to_hours.send_keys(to_time.split(":")[0])
    to_minutes.clear()
    to_minutes.send_keys(to_time.split(":")[1])

def select_month(month_to_select):
    current_month = datetime.now().month
    if month_to_select - current_month > 0:
        # Click next month
        click_element = browser.find_element_by_id("Header1_MonthAndYearBrowser1_imgbtnNextMonth")
    elif month_to_select - current_month < 0:
        # Click previous month
        click_element = browser.find_element_by_id("Header1_MonthAndYearBrowser1_imgbtnPrevMonth") 
    else:
        return
        
    for _ in range(abs(month_to_select - current_month)):
        click_element.click()
    
    
def fill_day(day_to_select, from_time, to_time):
    """
    Fills an entire work day.
    If the work day is more than 6 hours, add a 30 minutes break
    """
    global Config
    browser.switch_to_default_content()
    browser.switch_to.frame(browser.find_elements_by_tag_name("iframe")[3])
    browser.switch_to.frame(browser.find_elements_by_tag_name("frame")[1]) #u'frmHoursReportsDataEntry'
    
    select_day(day_to_select)
    
    from_time_datetime = datetime.strptime(from_time, HOUR_FORMAT)
    to_time_datetime = datetime.strptime(to_time, HOUR_FORMAT)
    tdelta = to_time_datetime - from_time_datetime
    
    project_name = Config.get(CONFIG_REPORT_SECTION, CONFIG_REPORT_PROJECT_NAME)
    task_name = Config.get(CONFIG_REPORT_SECTION, CONFIG_REPORT_TASK_NAME)
    description = Config.get(CONFIG_REPORT_SECTION, CONFIG_REPORT_DESCRIPTION)
    halfhour_description = Config.get(CONFIG_REPORT_SECTION, CONFIG_REPORT_HALFHOUR_DESCRIPTION)
    half_hour = Config.get(CONFIG_REPORT_SECTION, CONFIG_REPORT_HALFHOUR)
    
    if tdelta.seconds > 21600: # Bigger than 6 hours
        choose_project(project_name)
        choose_task(task_name)
        fill_description(description)
        choose_time(from_time, "12:00")
        save()
        
        choose_task(half_hour)
        fill_description(halfhour_description)
        choose_time("12:00", "12:30")
        save()
        
        choose_task(task_name)
        fill_description(description)
        choose_time("12:30", to_time)
        save()
    else:
        choose_task(task_name)
        choose_time(from_time, to_time)
        save()

def get_hours(monthday_element, selected_day):
    """
    Get a row in the table frmHoursReportList, return the time range in it
    """
    date_range = monthday_element.find_elements_by_tag_name("td")[4].text
    pattern = DATERANGE_REGEX.search(date_range)
    #from_time_datetime = datetime.strptime(pattern.group("from"), HOUR_FORMAT)
    #to_time_datetime = datetime.strptime(pattern.group("to"), HOUR_FORMAT)
    #TODO: should return the hours and not fill the day
    #fill_day(selected_day, pattern.group("from"), pattern.group("to"))
    return pattern.group("from"), pattern.group("to")

def add_break(day_to_select, selected_month):
    """
    Adds a half an hour break in a work day only if the work day is more than 6 hours
    """
    browser.switch_to_default_content()
    browser.switch_to.frame(browser.find_elements_by_tag_name("iframe")[3])
    browser.switch_to.frame(browser.find_elements_by_tag_name("frame")[0]) #u'frmHoursReportList'
    monthdays = browser.find_elements_by_class_name("seperateDay") # Work day row
    date_to_select = date(date.today().year, selected_month, day_to_select)
    
    # gridNoneWorkingDay
    found = False
    for i in range(2):
        if found == True:
            break
            
        for monthday_element in monthdays:
            if monthday_element.get_attribute("rowdate") == date_to_select.strftime("%Y%m%d"):
                from_hour, to_hour = get_hours(monthday_element, day_to_select)
                fill_day(day_to_select, from_hour, to_hour)
                found = True
                break

        browser.refresh() # Nothing was found, refresh

def save():
    save = browser.find_element_by_name("btnSaveNew")
    save.click()

def main():
    global Config
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(current_dir, CONFIG_FILENAME)
    Config.readfp(open(config_path))

    username = Config.get(CONFIG_LOGIN_SECTION, CONFIG_USERNAME)
    
    if Config.has_option(CONFIG_LOGIN_SECTION, CONFIG_PASSWORD):
        password = Config.get(CONFIG_LOGIN_SECTION, CONFIG_PASSWORD)
    elif Config.has_option(CONFIG_LOGIN_SECTION, CONFIG_BASE64PASSWORD): 
        password = Config.get(CONFIG_LOGIN_SECTION, CONFIG_BASE64PASSWORD).decode("base64")
    if password is None or password.strip() == '':
        password = getpass.getpass("Enter password: ")
    
    now = datetime.now()
    month = now.month if now.day > 5 else now.month-1
    
    browser.get(DESHE_CONNECTION_URL % (username, password) )
    select_month(month)
    browser.switch_to.frame(browser.find_elements_by_tag_name("iframe")[3])
    browser.switch_to.frame(browser.find_elements_by_tag_name("frame")[1]) #u'frmHoursReportsDataEntry'

    customer_name = Config.get(CONFIG_REPORT_SECTION, CONFIG_REPORT_CUSTOMER_NAME)
    choose_customer(customer_name)
    
    while True:
        result = raw_input("1. fill day, 2. add_break: ")
        if result == "1":
            day = raw_input("enter day: ")
            from_time = raw_input("enter from time: ")
            to_time = raw_input("enter to time: ")
            fill_day(day, from_time, to_time)
        elif result == "2":
            day = raw_input("enter day: ")
            add_break(int(day), month)
    browser.close()

    
if __name__ == "__main__":
    main()
