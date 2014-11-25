from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium import *
from time import sleep
import re
import os
import csv



# ##################Instructions for downloading sessions from Session IDs########################

# Using this python script requires that you have a CSV File of the relevant Session IDs you would like to download.
# You must create a file, 'sessionID.csv' and save it in the same directory where this python script is located.
# You must also make sure that in the same directory where you have this python script, you also have a folder (directory) named 'Data'.
# If you don't already have a folder 'Data', you should make one in this directory.
# 
# If all of the above prerequisites are complete, you should be okay to download. Make sure you have Firefox installed. You may consider changing the USERNAME, PASSWORD variables
# to your own credentials, as I currently have it set to my own: emericaism, emer1292.
# 
# In addition, if you are working from a Mac, you may encounter that on the very first session ID that is downloaded, Firefox will prompt you if you would like to open the
# file or if you would like to save it. You should select 'Save File' and 'Do this automatically from now on'. The script will pause for 10 seconds while
# it waits for the user to select 'Save File' and 'Do this automatically from now on'. The result should be that the remaining (n-1) downloads will happen automatically without interruption.
# 
# Expect this script to run at a rate of about 20 seconds per session downloaded.




#NOTE: This downloadSessions file should be in the same directory where you will be downloading the data to.

####PUT FILENAME OF CSV FILE CONTAINING LIST OF STUDY SESSION IDs#####
####CSV should have one column of data only, containing only names of files, no title.###
##The following codes simply reads off the data from rows 1 to end and adds them to the list of studies to search for.
csv_filename = 'sessionID.csv'
studyIDs = []
with open(csv_filename, 'rU') as csvfile:
    rowreader = csv.reader(csvfile, dialect='excel')
    currRow = 1
    for row in rowreader:
        studyIDs.append(row[0])
print studyIDs



#input parameter are the session ids as a list of ints
def downloadSession(sessionIDs):
    #login data
    USERNAME = 'emericaism'
    PASSWORD = 'emer1292'

    #check if temp folder exists. If not, we create it. Else, we will clear the contents of the temp folder, so as not to disrupt our process.
    if not os.path.exists(os.getcwd() + '/temp/'):
        os.makedirs(os.getcwd() + '/temp/')
    else:
        folder = os.getcwd() + '/temp/'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

    #check if Data base directory exists. If not, we make it.
    if not os.path.exists(os.getcwd() + '/Data/'):
        os.makedirs(os.getcwd() + '/Data/')


    #set target basedirectory
    baseDir = 'Data/'
    
    #update the firefox profile to make it automatically download all files that open download dialogs
    #files will be downloaded to cwd + "/temp" which needs to exist
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", os.getcwd() + '/temp')
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")# will always save into temp
    fp.set_preference("browser.helperApps.neverAsk.openFile", "text/plain")

    #start up a new Firefox
    driver = webdriver.Firefox(firefox_profile=fp)

    #Go to ladon admin console
    driver.get("http://ladon.mit.edu/admin/")

    #Find the box for the username click on it and enter the username
    inputElement = driver.find_element_by_name("username")
    inputElement.click()
    inputElement.send_keys(USERNAME)

    #Do the same thing for the Password
    inputElement = driver.find_element_by_name("password")
    inputElement.click()
    inputElement.send_keys(PASSWORD)

    #Submit the form (i.e. log in)
    inputElement.submit()


    iteration = 1
    #cycle the session IDs
    for curSessionID in sessionIDs:
        #go to the site of completed tasks for the current session
        driver.get('http://ladon.mit.edu/admin/mci/completedtask/?session__id__exact=' + str(curSessionID))
        
        #get the page source and find all session names
        pageSource = driver.page_source
        #sessionName = re.findall("Typing - Text[\S\s]+/\">([^\s]+)</a>[\s\S]+Introduction", pageSource)[0]

        #This Regex finds the line associated with a Contents as TXT link. Gets Name and Link. It happens that each data row is a single line in the source code.
        getAllContentsTXT = re.findall("(<tr class=\"grp-row grp-row.*?task/[0-9]+\">)(.*?)(</a>)[ \t\r\f\v\S]+(https?://[^\s]+?)\">Contents as TXT</a></td></tr>",pageSource)
        sessionName = re.findall("(<tr class=\"grp-row grp-row.*?nowrap\"><a.*?>(.*?)</a>.*?task/[0-9]+\">)(.*?)(</a>)[ \t\r\f\v\S]+(https?://[^\s]+?)\">Contents as TXT</a></td></tr>",pageSource)[0][1]
        
        #make sure the target folder exists
        if not os.path.exists(baseDir + sessionName):
            os.mkdir(baseDir + sessionName)

        #for all of the links (experiments), we will look for a txt file and try to download if such a file exists.
        for group in getAllContentsTXT:
            if len(getAllContentsTXT)==0:
                break
            #we can get the hashcode from the export link. Then, we will store it, since it is the file we are looking for in temp.
            currentLink = group[3]
            taskName = group[1]
            hashcode = re.search("(/p/)(.*?)(/export/txt)", currentLink).groups()[1]
            #we want fname to be fname = hashcode.txt
            fname = hashcode + '.txt'
            driver.get(currentLink)#this is the link to the export.
            sleep(1)

            #move the file to the target directory in the correct folder with the correct name            
            os.rename(os.getcwd() + '/temp/' + fname, baseDir + sessionName + '/' + taskName + ' ' + sessionName + '.txt')

    ###THIS CONCLUDES THE SECTION ON RETRIEVING TXT FILES

    ##WE NOW BEGIN THE SECTION ON RETRIEVING THE LOG FILE FROM LADON
        driver.get("http://ladon.mit.edu/mci/reporting/session/"+str(curSessionID)+"/export")

        #on my Mac, I was having problems with csv, because Firefox kept prompting if I wanted to open it.
        #On the first iteration, I have the script sleep for 6 seconds so that I can manually select "Save File. Don't ask this again."
        if iteration == 1:
            sleep(10)
            iteration = 2
        sleep(2)
        #move the file to the target directory in the correct folder with the correct name
        #fname = 'eventlog.csv'

        #because the hashcode for Ladon Log is not available, the best we can do is look for something that has '.csv'
        #I think this is actually safer than setting fname = 'eventlog.csv', because if the code tries to catch it before we finish
        #downloading it, we end up putting the wrong eventlog in the wrong study without the code breaking. That's pretty bad.
        #That said, I Really don't expect delays to be a problem, I have not had any on my computer. Nonetheless, I've added a print statement
        #to alert the user of such an error.
        i=0
        while True:
            if '.csv' in os.listdir(os.getcwd() + '/temp')[i]:
                fname = os.listdir(os.getcwd() + '/temp')[i]
                break
            else:
                i+=1
                print "MULTIPLE ITEMS IN /TEMP/ ERROR"
            if i==50:
                break

        os.rename(os.getcwd() + '/temp/' + fname, baseDir + sessionName + '/' + 'Ladon Log' + ' ' + sessionName + '.csv')

    ##WE NOW BEGIN THE SECTION ON RETRIEVING THE GRIDITEMS
        #goes to page with all griditems showing for this sessionID
        driver.get("http://ladon.mit.edu/admin/mci/completedtaskgriditem/?completed_task__session__id__exact="+str(curSessionID)+"&all=")
        #we find the checkbox for select all and click
        elements = driver.find_elements_by_xpath("/termin/input[@id='action-toggle']")
        elements[0].click()
        #At this point, we have selected all of the TaskGridItems.'
        #The following exports all of the griditems to a single csv file
        select_dropdown = driver.find_element_by_xpath("//option[@value='admin_list_export']")
        select_dropdown.click()
        sleep(2)
        #change fname to hash
        #fname = 'completedtaskgriditem.csv'

        #because the hashcode for Grid Items is not available, the best we can do is look for something that has '.csv'
        i=0
        while True:
            if '.csv' in os.listdir(os.getcwd() + '/temp')[i]:
                fname = os.listdir(os.getcwd() + '/temp')[i]
                break
            else:
                i+=1
                print "MULTIPLE ITEMS IN /TEMP/ ERROR"
            if i==50:
                break
        #fname = os.listdir(os.getcwd() + '/temp')[0]
        os.rename(os.getcwd() + '/temp/' + fname, baseDir + sessionName + '/' + 'Grid Items' + ' ' + sessionName + '.csv')

    #THIS IS THE END OF A GIVEN SESSIONID
    
    #close the webdriver
    driver.close()




if __name__ == '__main__':
    downloadSession(studyIDs)
    
