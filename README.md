<h1>Generating PDF Permit Reports with Python's Selenium.</h1>

<h2>Tools Used</h2>

- <b>Python</b>
- <b>WinSCP (FTP Script)</b>
- <b>SQL</b>
- <b>PowerShell</b>
- <b>SSMS (Scheduled Job)</b>
- <b>Windows Task Manager</b>

<h2>Description</h2>

<b> Problem: </b> The PAO wanted to display building permit data on the PAO website for the public to easily access from their account pages but was having trouble attaining the data. The permit data was accessible on a PDF report via an external webpage by searching with a parcel number but the public would have to be directed to that webpage and manually enter in their parcel number to get access to the permit report. This was extremely inconveniant and not user-friendly for the public.
<br><br>
 <b> Solution: </b> Created an automated process that uses the Python package Selenium to navigate a browser and interact with the webpage to generate 85,000+ pdf permit reports that are then FTP'd and made available on PAO website for the public to easily access and view.
 <br><br>
<b> Quick Overview:  </b>
 
  - <b>Step 1:</b> The list of accounts that need permit reports generated are exported monthly in a two column text file from SSMS via a Job. This text file contains PropertyIDs & ParcelIDs.
  - <b>Step 2:</b> A scheduled task runs a PowerShell script that kicks off the Python script.
  - <b>Step 3:</b> The Python script reads through the exported text file row by row entering the ParcelID into the webpage's search to generate and download the PDF report file, then renames the report as "PropertyID.pdf" after the file is downloaded in the network folder. This process is repeated until the count of pdf files in the folder matches the count of rows in the text file. Then the text file is deleted.
  - <b>Step 4:</b> A scheduled task runs twice a month that executes a WinSCP FTP script to ftp the PDF files to the PAO website where they can be accessed, viewed, and even downloaded by the public.

<p align="center">
<img src="https://i.imgur.com/jaZSV2w.png" height="75%" width="75%" alt="Permit Report Process Flowchart"/>
</p>

I am always looking for ways to improve this process. Currently, the Python script generates and downloads 85,000+ pdf report files in just under 75 hours. Then because I can't unzip folders on the FTP site the pdf files are individually FTP'd taking another 25 hours. This results in the entire process taking about 100 hours from the creation of the first report to the last report being made available on the PAO website.

Here's a live look at one of the pdf permit reports on the website: [https://mcpaofiles.com/permits/7.pdf](https://mcpaofiles.com/permits/7.pdf)

<h2>The Good Stuff</h2>

The following items are present in the python code involved:

- Selenium
- Logging
- Try-Except Error Handling
- If / Else Logic
- While Loop

The following items are present in the SQL stored procedure involved:

- #Temp Tables
- Indexing

Links to SQL scripts involved in this process:
- [Export Data to CSV](https://github.com/Deltron2020/ExportDataToCsv)

