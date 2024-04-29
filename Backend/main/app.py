from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import PyPDF2
import openai
import time
import concurrent.futures 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import base64 
import urllib.parse

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variable to store the API key
api_key = None

# Paths to the LaTeX template files
start_template_path = os.path.join(os.path.dirname(__file__), 'latex_resume_format_start.tex')
end_template_path = os.path.join(os.path.dirname(__file__), 'latex_resume_format_end.tex')
cover_letter_start_template_path = os.path.join(os.path.dirname(__file__), 'latex_cover_letter_format_start.tex')
cover_letter_end_template_path = os.path.join(os.path.dirname(__file__), 'latex_cover_letter_format_end.tex')

with open(start_template_path, 'r') as file:
    start_template = file.read()

with open(end_template_path, 'r') as file:
    end_template = file.read()

with open(cover_letter_start_template_path, 'r') as file:
    cover_letter_start_template = file.read()

with open(cover_letter_end_template_path, 'r') as file:
    cover_letter_end_template = file.read()

# Global variable to store the resume text
resume_text = None

# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return str(e)

def create_latex_resume_assistant():
    client = openai.Client(api_key=api_key)  # Pass api_key to the client
    assistant = client.beta.assistants.create(
        model="gpt-4-1106-preview",
        name="LaTeX Resume Content Integrator",
        instructions="""Integrate the user's resume details into the 'latex_end_template', adhering strictly to its structure and format.
        Start from \begin{document}, and ensure the content aligns with the provided LaTeX commands and sections.
        Focus on the Experience, Education, Projects, and Technical Skills sections, using the user's resume information.
        Avoid any unicode characters and extra LaTeX commands not present in the template.
        If specific data (like project dates) are absent in the user's resume, omit those elements from the template. Highlight in bold any resume content that matches key terms in the job description,
        particularly in the Experience and Projects sections. Tailor the resume to emphasize aspects relevant to the job description, without adding information not present in the user's resume.
        The output should form a one-page, fully formatted LaTeX document, ready to merge into a complete resume. also dont write ```latex at the start and ``` at the end. Make sure to use only this apostrophe ' and only this dash - not any other ones.""",
        tools=[]
    )
    return assistant

def create_latex_cover_letter_assistant():
    client = openai.Client(api_key=api_key)  # Pass api_key to the client
    assistant = client.beta.assistants.create(
        model="gpt-4-1106-preview",
        name="LaTeX Cover Letter Content Integrator",
        instructions="""Integrate the user's resume details and job description into the 'latex_cover_letter_end_template', adhering strictly to its structure and format.
        Start from \begin{document}, and ensure the content aligns with the provided LaTeX commands and sections.
        Focus on creating a compelling introduction, highlighting relevant skills and experiences, and expressing enthusiasm for the position and company.
        Avoid any unicode characters and extra LaTeX commands not present in the template.
        If specific data is absent in the user's resume or job description, gracefully handle the omission. 
        The output should form a one-page, fully formatted LaTeX document, ready to merge into a complete cover letter. 
        Do not write ```latex at the start and ``` at the end. Make sure to use only this apostrophe ' and only this dash - not any other ones.""",
        tools=[]
    )
    return assistant



def generate_latex_resume_from_input(user_resume, job_description, latex_end_template, assistant_id):
    client = openai.Client(api_key=api_key)  # Pass api_key to the client
    print("[Debug] Creating a thread for conversation...")
    thread = client.beta.threads.create()
    thread_id = thread.id
    print(f"[Debug] Thread created with ID: {thread_id}")

    print("[Debug] Adding messages to the thread...")
    messages = [
        {"role": "user", "content": user_resume},
        {"role": "user", "content": job_description},
        {"role": "user", "content": latex_end_template}
    ]
    for message in messages:
        print(f"[Debug] Adding message with role '{message['role']}'")
        client.beta.threads.messages.create(thread_id=thread_id, role=message["role"], content=message["content"])

    print("[Debug] Running the assistant with the created thread...")
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    while run.status in ['queued', 'in_progress']:
        print(f"[Debug] Waiting for run to complete... Status: {run.status}")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    print(f"[Debug] Run status after completion: {run.status}")
    if run.status == 'completed':
        print("[Debug] Run completed. Fetching messages...")
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages.data:
            print(f"[Debug] Message role: {message.role}")
            if message.role == "assistant":
                print("[Debug] Assistant message found. Checking for LaTeX content...")
                if isinstance(message.content, list):
                    # Iterate through the list of content parts
                    for part in message.content:
                        if isinstance(part, openai.types.beta.threads.message_content_text.MessageContentText):
                            response_text = part.text.value
                            print("[Debug] Generated LaTeX content:")
                            print(response_text)
                            if response_text.strip():
                                return response_text
                else:
                    print(f"[Debug] Unexpected content type received from the assistant: {type(message.content)}")
            else:
                print(f"[Debug] Message from role '{message.role}' received.")
    else:
        print(f"[Debug] Run did not complete successfully. Status: {run.status}")

    print("[Debug] No valid LaTeX content found or run did not complete successfully.")
    return None


def generate_latex_cover_letter_from_input(user_resume, job_description, latex_cover_letter_end_template, assistant_id):
    client = openai.Client(api_key=api_key)  # Pass api_key to the client
    print("[Debug] Creating a thread for conversation (cover letter)...")
    thread = client.beta.threads.create()
    thread_id = thread.id
    print(f"[Debug] Thread created with ID: {thread_id}")

    print("[Debug] Adding messages to the thread (cover letter)...")
    messages = [
        {"role": "user", "content": user_resume},
        {"role": "user", "content": job_description},
        {"role": "user", "content": latex_cover_letter_end_template}
    ]
    for message in messages:
        print(f"[Debug] Adding message with role '{message['role']}'")
        client.beta.threads.messages.create(thread_id=thread_id, role=message["role"], content=message["content"])

    print("[Debug] Running the assistant with the created thread (cover letter)...")
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    while run.status in ['queued', 'in_progress']:
        print(f"[Debug] Waiting for run to complete... Status: {run.status}")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    print(f"[Debug] Run status after completion: {run.status}")
    if run.status == 'completed':
        print("[Debug] Run completed. Fetching messages...")
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages.data:
            print(f"[Debug] Message role: {message.role}")
            if message.role == "assistant":
                print("[Debug] Assistant message found. Checking for LaTeX content...")
                if isinstance(message.content, list):
                    # Iterate through the list of content parts
                    for part in message.content:
                        if isinstance(part, openai.types.beta.threads.message_content_text.MessageContentText):
                            response_text = part.text.value
                            print("[Debug] Generated LaTeX content:")
                            print(response_text)
                            if response_text.strip():
                                return response_text
                else:
                    print(f"[Debug] Unexpected content type received from the assistant: {type(message.content)}")
            else:
                print(f"[Debug] Message from role '{message.role}' received.")
    else:
        print(f"[Debug] Run did not complete successfully. Status: {run.status}")

    print("[Debug] No valid LaTeX content found or run did not complete successfully.")
    return None


def combine_and_save_latex_resume(start_content, generated_content):
    combined_content = start_content + '\n' + generated_content

    # Encode LaTeX content to Base64 and URL-encode the result
    encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')
    url_encoded_content = urllib.parse.quote(encoded_content)  # URL encode the Base64 string

    data_url = f"data:application/x-tex;base64,{url_encoded_content}"

    return data_url  # Return the data URL directly


def combine_and_save_latex_cover_letter(start_content, generated_content):
    combined_content = start_content + '\n' + generated_content

    # Encode LaTeX content to Base64 and URL-encode the result
    encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')
    url_encoded_content = urllib.parse.quote(encoded_content)  # URL encode the Base64 string

    data_url = f"data:application/x-tex;base64,{url_encoded_content}"

    return data_url  # Return the data URL directly


# Function to click "Show More Jobs" on the webpage
def click_show_more_jobs(driver):
    try:
        for _ in range(1):
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, 'moreresultbutton')))
            show_more_button = driver.find_element(By.ID, 'moreresultbutton')
            show_more_button.click()
            time.sleep(2)
    except (NoSuchElementException, TimeoutException):
        print("Show more jobs button not found, not clickable, or no more jobs to load.")
    except Exception as e:
        print(f"An error occurred while clicking the button: {e}")

# Function to scrape job bank links
def scrape_job_bank_links(driver, url):
    job_links = []
    try:
        # Ensure the URL is valid
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError(f"Invalid URL: {url}")

        driver.get(url)
        time.sleep(5)

        click_show_more_jobs(driver)

        job_postings = driver.find_elements(By.CSS_SELECTOR, "div#ajaxupdateform\\:result_block article a.resultJobItem")
        for job in job_postings:
            link = job.get_attribute('href')
            job_links.append(link)

    except Exception as e:
        print(f"An error occurred while scraping job links: {str(e)}")
    finally:
        return job_links


def create_email_assistant():
    client = openai.Client(api_key=api_key)
    assistant = client.beta.assistants.create(
        model="gpt-4-1106-preview",  # Or a suitable model for email generation
        name="Job Application Email Generator",
        instructions="""Generate a professional email body for a job application. 
        Use the user's resume and the job description to highlight relevant skills and experiences. 
        Express enthusiasm for the position and company. Keep the tone formal and concise.""",
        tools=[]
    )
    return assistant

def generate_email_body(user_resume, job_details, assistant_id):
    client = openai.Client(api_key=api_key)
    thread = client.beta.threads.create()
    thread_id = thread.id

    messages = [
        {"role": "user", "content": user_resume},
        {"role": "user", "content": job_details},
        {"role": "user", "content": "Please generate a professional email body for a job application based on the provided resume and job details."}
    ]
    for message in messages:
        client.beta.threads.messages.create(thread_id=thread_id, role=message["role"], content=message["content"])

    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    while run.status in ['queued', 'in_progress']:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages.data:
            if message.role == "assistant":
                if isinstance(message.content, list):
                    for part in message.content:
                        if isinstance(part, openai.types.beta.threads.message_content_text.MessageContentText):
                            email_body_text = part.text.value
                            if email_body_text.strip():
                                return email_body_text
                else:
                    print(f"[Debug] Unexpected content type received from the assistant: {type(message.content)}")
            else:
                print(f"[Debug] Message from role '{message.role}' received.")
    else:
        print(f"[Debug] Run did not complete successfully. Status: {run.status}")

    return None  # Return None if no email body could be generated



# Function to process a single job link
def process_job_link(job_link):
    driver = None
    try:
        chrome_options = webdriver.ChromeOptions()
        # Uncomment for headless mode
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(job_link)
        time.sleep(2)

        # Click the "Show how to apply" button and get the email
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'applynowbutton')))
        apply_button = driver.find_element(By.ID, 'applynowbutton')
        apply_button.click()
        time.sleep(2)

        email_element = driver.find_element(By.CSS_SELECTOR, "div#howtoapply a[href^='mailto']")
        email = email_element.text if email_element else "Not specified"

        # Scrape the job description and remove newline characters
        job_description_element = driver.find_element(By.CSS_SELECTOR, "div.job-posting-detail-requirements")
        job_description = job_description_element.text.replace('\n', ' ') if job_description_element else "Not specified"

        # Extract additional details
        position_element = driver.find_element(By.CSS_SELECTOR, "h1[property='name'] span[property='title']")
        position = position_element.text.strip() if position_element else "Not specified"

        company_element = driver.find_element(By.CSS_SELECTOR, "span[property='hiringOrganization'] span[property='name'] a")
        company_name = company_element.text.strip() if company_element else "Not specified"
        company_link = company_element.get_attribute('href').strip() if company_element else "Not specified"

        pay_element = driver.find_elements(By.CSS_SELECTOR, "span[property='baseSalary'] span[property='value']")
        pay = f"{pay_element[0].text} to {pay_element[1].text}" if len(pay_element) > 1 else (pay_element[0].text if pay_element else "Not specified")

        location_element = driver.find_element(By.CSS_SELECTOR, "span[property='joblocation'] span[property='addressLocality']")
        location = location_element.text.strip() if location_element else "Not specified"

        # Add 'job_link' to the dictionary
        return {
            'company_name': company_name,
            'position': position,
            'pay': pay,
            'location': location,
            'job_link': job_link,
            'job_email': email,
            'job_description': job_description,
            'company_link': company_link,
        }
    except Exception as e:
        print(f"Error processing {job_link}: {str(e)}")
        return {
            'company_name': None,
            'position': None,
            'pay': None,
            'location': None,
            'job_link': job_link,
            'job_email': None,
            'job_description': None,
            'company_link': None,
        }
    finally:
        if driver:
            driver.quit()

# Function to scrape emails in parallel
def scrape_emails_in_parallel(job_links):
    batch_size = 10
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(0, len(job_links), batch_size):
            batch_links = job_links[i:i + batch_size]
            futures = [executor.submit(process_job_link, link) for link in batch_links]
            batch_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            yield batch_results

def get_job_link_from_resume(resume_text):
    client = openai.Client(api_key=api_key)
    completion = client.chat.completions.create(  # Pass api_key here
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a link creation bot. ONLY RESPOND WITH LINK. You will be making the link based on the resume that the user provides. dont say here's the link or anything like that just the link and only the link should be returned back. ONLY THE LINK NEEDS TO BE RETURNED. You will be responding only with Canada job bank links and nothing else. Here are some example links: This one is for a software developer in Toronto: https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=software+developer&locationstring=toronto, This one is for a receptionist located in Alberta: https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=receptionist&locationstring=alberta . If the resume is of a certain major like industrial engineering for example provide me the link for possible positions that the industrial engineer might work as and not just industrial engineer in the link."},
            {"role": "user", "content": resume_text}
        ]
    )
    return completion.choices[0].message.content

# Route to generate cover letter
@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter_route():
    data = request.json  # Receive job details and resume text from frontend
    job_details = data.get('jobItem')
    
    if not job_details:
        return jsonify(error="Missing required data: resume text and job details"), 400

    latex_cover_letter_assistant = create_latex_cover_letter_assistant()
    generated_latex_content = generate_latex_cover_letter_from_input(
        resume_text, str(job_details), cover_letter_end_template, latex_cover_letter_assistant.id
    )
    
    if generated_latex_content is None:
        return jsonify(error="Failed to generate LaTeX cover letter"), 500

    cover_letter_path = combine_and_save_latex_cover_letter(cover_letter_start_template, generated_latex_content)
    return jsonify(cover_letter=cover_letter_path)


# Route to generate resume
@app.route('/generate-resume', methods=['POST'])
def generate_resume_route():
    job_details = request.json  # Assuming the frontend sends the job details in JSON format
    
    # Debug: Check if global variable resume_text is None
    global resume_text
    if resume_text is None:
        print("Error: resume_text is None.")
        return jsonify(error="Resume text is not available"), 400
    else:
        print(f"resume_text length: {len(resume_text)}")

    # Debug: Check the job_details content
    if job_details is None:
        print("Error: job_details is None.")
        return jsonify(error="Job details are not provided"), 400
    print(f"Job Details: {job_details}")

    # Generate LaTeX resume using the second code's functionality
    latex_resume_assistant = create_latex_resume_assistant()
    print(f"Assistant ID: {latex_resume_assistant.id}")  # Debug: Print assistant ID

    generated_latex_content = generate_latex_resume_from_input(resume_text, str(job_details), end_template, latex_resume_assistant.id)
    if generated_latex_content is None:
        print("Error: Generated LaTeX content is None.")
        return jsonify(error="Failed to generate LaTeX resume"), 500

    resume = combine_and_save_latex_resume(start_template, generated_latex_content)

    return jsonify(resume=resume)


@app.route('/images', methods=['POST'])
def upload_image():
    global resume_text  # Declare the global variable at the start of the function
    if 'image' in request.files:
        file = request.files['image']
        resume_text = extract_text_from_pdf(file)
        print(f"Resume text extracted: {resume_text[:500]}")  # Print first 500 characters for verification

        if resume_text:
            # Get job link from OpenAI
            job_link = get_job_link_from_resume(resume_text)
            print(f"Job link: {job_link}")

            # Start the Selenium job scraping process
            try:
                driver = webdriver.Chrome()
                job_links = scrape_job_bank_links(driver, job_link)
                driver.quit()

                # Process and return job details in batches
                all_results = []
                for batch_results in scrape_emails_in_parallel(job_links):
                    print(batch_results)  # Handle each batch as needed
                    filtered_results = [res for res in batch_results if not any(v is None for v in res.values())]
                    all_results.extend(filtered_results)

                return jsonify(emailResults=all_results)
            except Exception as e:
                print(f"An error occurred during job scraping: {e}")
                return jsonify(error='An error occurred during job scraping'), 500
        else:
            return jsonify(error='Failed to extract text from resume'), 400
    else:
        return jsonify(error='No resume provided'), 400

@app.route('/download-resume-pdf', methods=['GET'])
def download_resume_pdf():
    pdf_file_path = os.path.join(os.path.dirname(__file__), 'generated_resume.pdf')
    return send_file(pdf_file_path, as_attachment=True)

@app.route('/download-cover-letter-pdf', methods=['GET'])
def download_cover_letter_pdf():
    pdf_file_path = os.path.join(os.path.dirname(__file__), 'generated_cover_letter.pdf')
    return send_file(pdf_file_path, as_attachment=True)


@app.route('/generate-email', methods=['POST'])
def generate_email_route():
    data = request.json
    job_item = data.get('jobItem')
    # ... error handling for missing job details

    email_assistant = create_email_assistant()
    email_body = generate_email_body(resume_text, str(job_item), email_assistant.id)
    return jsonify(emailBody=email_body, recipientEmail=job_item.get('job_email'))



# Route to receive and set the API key
@app.route('/set-api-key', methods=['POST'])
def set_api_key():
    global api_key
    data = request.json
    api_key = data.get('apiKey')
    if api_key:
        openai.api_key = api_key  # Set the OpenAI API key
        print("API key set successfully.")
        return jsonify(message="API key set successfully")
    else:
        print("Error: API key not provided.")
        return jsonify(error="API key not provided"), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)