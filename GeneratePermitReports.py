import sys
sys.path.append(r'\\network_path\PermitReportSearch\venv\Lib\site-packages')
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.options import Options
import logging
import time
import os

log_file = r'\\network_path\Permit_Report_Search\log.log'
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')    #logging.DEBUG
exceptionCount = 0

downloadPath = r'\\network_path\permits'
parcelIdFile = r'\\network_path\permit_reports\Permit_Report_Account_List.txt'

options = webdriver.ChromeOptions()
options.add_argument("--headless")
prefs = {
        "download.default_directory" : downloadPath,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True
         }

options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


def FolderFileCount(path, extension):
        count = 0
        list = os.listdir(path)
        for file in list:
                if file.endswith(extension):
                        count+=1
                else:
                        continue
        return count


def DeleteFiles(path):
        deleteList = os.listdir(path)
        for file in deleteList:
            if file.endswith('.pdf'):
                try:
                    os.remove(rf'{path}\{file}')
                except PermissionError as pe:
                    logging.info('** Issue deleting files - Permission Error: Access Denied  - program terminated **')
                    logging.exception(pe)
                    exit()
                except Exception as e:
                    logging.info('** Issue deleting files - program terminated **')
                    logging.exception(e)
                    exit()


def send_email(receiver, subject):
    # https://leimao.github.io/blog/Python-Send-Gmail/
    import smtplib, ssl
    from email.message import EmailMessage

    port = 465  # For SSL
    smtp_server = ""
    sender_email = ""  # Enter your address
    password = ""

    msg = EmailMessage()
    msg.set_content(log_file)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg, from_addr=sender_email, to_addrs=receiver)


##################################
logging.info('***BEGINNING PROCESS: Attempting to Read File...***')
send_email('tyler@gmail.com', 'BEGINNING PERMIT REPORT PROCESS')
start_time = time.time()
#################################

# 1 - Delete all files in the download folder
DeleteFiles(downloadPath)

# 2 - then get a count of files remaining
originalReportCount = FolderFileCount(downloadPath, '.pdf')

# 3 - if exists check > if not send email
if os.path.exists(parcelIdFile) and os.path.exists(downloadPath):
        pass
else:
        logging.info('***The parcelIdFile OR the downloadPath does not exist or the path was entered incorrectly - program terminated ***')
        send_email('tyler@gmail.com','***Change Of Address Report Failure***')
        exit()

try:
    # 4- open txt file and import data into list
    with open(parcelIdFile,'r') as rf:
            parcelIdList = []
            for pID in rf:
                pID = pID.strip()
                pID = pID.rsplit('|')
                parcelIdList.append(pID)

    totalParcelCount = len(parcelIdList)
except Exception as e:
    logging.info('** Issue opening Parcel ID file - program terminated **')
    logging.exception(e)
    exit()


# 5 - first loop through all accounts in list, errors are counted & logged then loop moves to next item in list
for ids in parcelIdList:
    parcelId = ids[0].strip()
    propertyId = ids[1].strip()
    try:
        driver.get("https://aca-prod.accela.com/MARTINCO/Report/ReportParameter.aspx?module=&reportID=30728&reportType=LINK_REPORT_LIST")

        time.sleep(.5)

        parcelSearchBox = driver.find_element(By.ID, "SessionVariable_34450")  # search bar
        parcelSearchBox.send_keys(parcelId)

        driver.find_element(By.ID, "btnSave").click()  # submit

        time.sleep(2.0)

        oldName = fr"{downloadPath}\CrystalViewer.pdf"
        newName = fr"{downloadPath}\{propertyId}.pdf"

        try:
            os.rename(oldName, newName)
        except:
            logging.info('* Rename Failed *')
            continue

    except Exception as e:
        exceptionCount += 1
        logging.info(f'Permit Report Not Created For Account: {propertyId}')
        continue

logging.info('** NOW ENTERING WHILE LOOP **')

# 6 - second loop through all accounts in list, uses while loop until parcel id count in file matches count of pdf files in folder
while FolderFileCount(downloadPath, '.pdf') < totalParcelCount:
    try:
        # create a list of pdfs in download folder
        pdfList = os.listdir(downloadPath)
        for x, i in enumerate(pdfList):
            if i.endswith('.pdf'):
                i = i.replace('.pdf', '')
                pdfList[x] = i
            else:
                pdfList.remove(i)
                continue

        for ids in parcelIdList:
            parcelId = ids[0].strip()
            propertyId = ids[1].strip()
            if propertyId in pdfList:
                parcelIdList.remove(ids)
                continue
            else:
                try:
                    driver.get("https://aca-prod.accela.com/MARTINCO/Report/ReportParameter.aspx?module=&reportID=30728&reportType=LINK_REPORT_LIST")

                    time.sleep(.5)

                    parcelSearchBox = driver.find_element(By.ID, "SessionVariable_34450")  # search bar
                    parcelSearchBox.send_keys(parcelId)

                    driver.find_element(By.ID, "btnSave").click()  # submit

                    time.sleep(2.0)

                    oldName = fr"{downloadPath}\CrystalViewer.pdf"
                    newName = fr"{downloadPath}\{propertyId}.pdf"

                    try:
                        os.rename(oldName, newName)
                    except:
                        logging.info('* Rename Failed *')
                        continue

                except Exception as e:
                    exceptionCount += 1
                    logging.info(f'Permit Report Not Created For Account: {propertyId}')
                    continue

    except Exception as e:
        logging.exception(e)
        if exceptionCount > 1000: #arbitray number, but should keep script from running forever if the url goes down
            logging.info('** PROCESS TERMINATED - EXCEPTION COUNT EXCEEDED 1000')
            send_email('tyler@gmail.com', 'EXCEPTION COUNT EXCEEDED 1000')
            exit()
        else:
            continue


# 7 - cleanup >> delete accounts list txt file to allow FTP script to begin
try:
    os.remove(parcelIdFile)
except Exception as e:
    logging.info('** Issue deleting parcelIDFile **')
    logging.exception(e)
    send_email('tyler@gmail.com', 'Issue deleting parcelIDFile')


# count of files in folder after process finished
finalReportCount = FolderFileCount(downloadPath, '.pdf')
end_time = time.time()
execution_time = round(((end_time - start_time)/60)/60,4)

logging.info(f'Total pdf files in folder before review: {originalReportCount}')
logging.info(f'Total pdf files in folder after review: {finalReportCount}')
logging.info(f'Total Parcel IDs in file: {totalParcelCount}')
logging.info(f'Total Exceptions Occurred: {exceptionCount}')
logging.info(f'Total Run Time: {execution_time} hours')

send_email('tyler@gmail.com', 'ENDING PERMIT REPORT PROCESS')

#################################
logging.info('***PROCESS COMPLETE***')
#################################

driver.close()
driver.quit()

exit()
