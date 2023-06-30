#libraries
import requests    
import xml.etree.ElementTree as ET
from openpyxl import Workbook

def get_feed_data(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.content
    else:
        return None

#extracting data feed url
feed_url = "https://feeds.bbci.co.uk/news/rss.xml"  #feed xml link
feed_data = get_feed_data(feed_url)

if feed_data:
    root = ET.fromstring(feed_data)
    
    # Create a new Excel workbook and select the active sheet
    workbook = Workbook()
    sheet = workbook.active
    
    # Write headers
    headers = ['Title', 'Link', 'Description', 'Publication Date']
    sheet.append(headers)
    
    # Iterate over items and write data to rows, extracting data
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text
        pub_date = item.find('pubDate').text
        
        row_data = [title, link, description, pub_date]
        sheet.append(row_data)
    
    # Save the workbook to a file, saving in excel
    output_file = "feed_data.xlsx"  # Output file name
    workbook.save(output_file)
    
    print(f"Feed data written to '{output_file}' successfully.")
else:
    print("Failed to retrieve feed data.")
