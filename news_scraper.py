import smtplib

from serpapi import GoogleSearch

import sys

import io

import datetime

import csv

from dotenv import load_dotenv

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

#Environment variables
load_dotenv()
SERP_API_KEY = os.getenv('API_KEY')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('PASS')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')

# Fetches search queries using SERP api 
#Documentation: https://serpapi.com/search-api
#https://github.com/serpapi/google-search-results-python
def fetch_search_results(queries):
    all_results = []
    for query in queries:
        results = []
        params = {
            "api_key": SERP_API_KEY,
            "q": query,
            "tbm": 'nws',
            "as_qdr": "w1",  # Filter for results from the past week
            "as_q": '"high school" OR college OR university',
            "num": 20
        }
        
        
        try:
            search = GoogleSearch(params)
            data = search.get_dict()
            if "error" in data:
                raise Exception("Error accessing API")
            print("Successful API connection")
            for result in data["news_results"]:
                results.append([result["title"], result["link"], result["date"]])
            all_results.extend(results)
            
        except Exception as e:
            print(f"Error: {e}")
    
    return all_results


def save_search_results_to_csv(results):
    csv_temp = io.StringIO()
    csv_writer = csv.writer(csv_temp)
    for entry in results:
        csv_writer.writerow(entry)
    csv_data = csv_temp.getvalue()
    csv_temp.close()
    return csv_data
    
def send_result(recipient, subject, message, csv_data, file_name):
    
    body = message
    
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg.attach(MIMEText(body, "plain"))
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(csv_data)
    
    encoders.encode_base64(attachment)
    
    file_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    
    attachment.add_header("Content-Disposition", f"attachment; filename= {file_name}_{file_time}")
    
    
    msg.attach(attachment)
    
    
    try: 
        print("Connecting...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, PASSWORD)
            print("Connected!")
            print("\nSending email...")
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        print("Successfully sent!")
    except Exception as e:
        print(f"Failed: {e}")
        
#topic_tokens are the queries
#recipient_email is the receiving email address
#subject is the subject of the email
#message is the message of the email
#output_filename is the name of the file attachment being sent in the email

def main(topic_tokens, recipient_email, subject, message, output_filename):
    tokens = topic_tokens.split(",")
    news = fetch_search_results(tokens)
    saved_results_csv = save_search_results_to_csv(news)
    send_result(recipient_email, subject, message, saved_results_csv, output_filename)
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Arguments inputted incorrectly. Please check if you have the correct number of input arguments.")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])    
    