
#! /usr/bin/env python

import os
import sys
import re
import json
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from pypdf import PdfMerger
from canvasapi import Canvas
from tkinter import Tcl
import dotenv
import requests
import smtplib, ssl

def main():
    try:
        # Load environment variables
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)

        API_URL = os.getenv("API_URL")
        API_KEY = os.getenv("API_KEY")
        COURSE_ID = os.getenv("COURSE_ID")
        INSTITUTION_URL = os.getenv("INSTITUTION_URL")
        NOTE_FOLDER_DIRECTORY = os.path.join(os.getcwd(), "notes")
        COMBINED_NOTES_DIRECTORY = os.path.join(os.getcwd(), "output", "combined_notes.pdf")
        SENDER_EMAIL = os.getenv("SENDER_EMAIL")
        RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
        EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

        if not all([API_URL, API_KEY, COURSE_ID, INSTITUTION_URL, NOTE_FOLDER_DIRECTORY, COMBINED_NOTES_DIRECTORY, SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_PASSWORD]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

        # Ensure directories exist
        os.makedirs(NOTE_FOLDER_DIRECTORY, exist_ok=True)
        os.makedirs(os.path.dirname(COMBINED_NOTES_DIRECTORY), exist_ok=True)

        print("Step 1: Logging into Canvas API")
        canvas = Canvas(API_URL, API_KEY)
        course = canvas.get_course(COURSE_ID)
        print("Logged in successfully!")

        try:
            list_var = [int(module_id) for module_id in json.loads(os.getenv('MODULE_ITEM_IDS', '[]'))]
        except json.JSONDecodeError:
            dotenv.set_key(dotenv_file, "MODULE_ITEM_IDS", '[]')
            list_var = []

        print(f"Modules in the course ({course.name}):")
        i_count = 0
        for module in course.get_modules():
            print(f"Module: {module.name}")
            for module_item in module.get_module_items():
                if re.search("^Lecture", module_item.title):
                    if module_item.id not in list_var:
                        list_var.append(module_item.id)
                        print(f"New lecture found: {module_item.title} (ID: {module_item.id})")
                        
                        module_item_query = requests.get(
                            f"{API_URL}/courses/{COURSE_ID}/modules/{module.id}/items/{module_item.id}",
                            headers={"Authorization": f"Bearer {API_KEY}"}
                        )
                        module_item_query_json = module_item_query.json()
                        file_query = requests.get(module_item_query_json['url'], headers={"Authorization": f"Bearer {API_KEY}"})
                        body_json = file_query.json().get('body', '')
                        wrapper_url = re.search(r"https://[^ ]+", body_json).group(0)
                        wrapper_query = requests.get(wrapper_url, headers={"Authorization": f"Bearer {API_KEY}"})
                        soup = BeautifulSoup(wrapper_query.text, 'html.parser')
                        download_link = soup.find('a', href=re.compile("/files/"))['href']
                        file_link = INSTITUTION_URL + download_link
                        file_path = os.path.join(NOTE_FOLDER_DIRECTORY, f"L{i_count + 1}.pdf")
                        urlretrieve(file_link, file_path)
                        i_count += 1

        dotenv.set_key(dotenv_file, "MODULE_ITEM_IDS", json.dumps(list_var))
        merge_notes(NOTE_FOLDER_DIRECTORY, COMBINED_NOTES_DIRECTORY)

    except Exception as e:
        print(f"An error occurred: {e}")
        send_error_email(SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_PASSWORD, str(e))


def merge_notes(note_folder, output_file):
    print("Merging notes...")
    lecture_notes = PdfMerger()
    sorted_files = Tcl().call('lsort', '-dict', os.listdir(note_folder))
    for notes in sorted_files:
        if notes.endswith('.pdf'):
            lecture_notes.append(os.path.join(note_folder, notes))
    lecture_notes.write(output_file)
    print(f"Notes merged into {output_file}")


def send_error_email(sender, receiver, password, error_message):
    subject = "Error in Notes Synthesizer"
    message = f"Subject: {subject}\n\nAn error occurred:\n\n{error_message}"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message)
    print(f"Error email sent to {receiver}")


if __name__ == "__main__":
    main()
