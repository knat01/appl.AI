import openai
import os
import time

# Initialize OpenAI API key

user_resume_text = """
Shaun Sequeira
 437-971-7883 # shaun.sequeira88@gmail.com ï linkedin.com/in/shaunsequeira08 § github.com/knat01
Experience
Royal Bank of Canada August 2022 - August 2023
Full Stack Developer Toronto, ON
• Led the development of an application, streamlining the data transfer process for RBC employees. Automated
data transfer and permission handling, reducing file transfer time from one week to immediate action.
• Enabled instant file transfers to AWS S3 and Snowflake, boosting productivity by allowing users to
independently request access and transfer files.
• Designed and implemented a secure service layer using Python for managing user access requests and
approvals, facilitating authorization of data movement to the cloud.
• Architected a comprehensive database schema in PostgreSQL, focusing on performance and scalability.
• Developed a web application using React and TypeScript, enabling 1000+ employees in the Tech&Ops
department to request data transfer permissions and send data directly to S3 buckets and Snowflake.
• Containerized the application using Docker, enhancing operational efficiency and streamlining deployment.
• Utilized Airflow for automating complex workflows, enhancing efficiency and integrating seamlessly with
various AWS services including S3 and Snowflake.
• Hands-on experience in setting up and managing multiple CI/CD pipelines, ensuring efficient and reliable
software delivery to production environments.
• Employed Grafana for monitoring and visualization, aiding in performance optimization and health tracking
Education
Toronto Metropolitan University August 2019 - April 2024
Bachelor of Science in Computer Science Toronto, ON
Projects
Appl.ai | Python, Selenium, OpenAI GPT, LLAMA
• A platform that automates job searching by analyzing user resumes and finding relevant job listings.
• Integrated OpenAI's GPTs and LLAMA models to automatically generate custom ATS scannable resumes
and cover letters, tailored for each job description and the user's work experience.
• Implemented a web scraper using Selenium to extract job postings from various online job boards, matching
them with the user's skills and experience.
• Designed the platform to parse and interpret user resumes using Python, extracting key information to align
with job requirements.
Function Calling Model | Python, GPT-3.5, GPT-4, Mistral
• Collaborated with a colleague to design a model for generating function calls in software applications,
enhancing workflow efficiency.
• Curated training datasets from custom files and outputs of LLMs such as GPT-3.5, GPT-4, and Mistral.
• Implemented robust preprocessing techniques to standardize text data, ensuring optimal model training.
• Conducted rigorous testing procedures together to validate the model's accuracy, functionality, and reliability
across a wide range of scenarios.
Technical Skills
Languages: Python, C++, C , JavaScript, TypeScript, SQL, HTML, CSS, PHP, MATLAB, Java
Frameworks/Libraries: Node.js, Boto3, React, FastAPI, Flask, LLAMA 2, CodeLLama
Infrastructure: Amazon S3, Kubernetes, Shopify, Postgres, MS Office, Wordpress, Docker, AWS Lambda
Developer Tools: VS Code, Github, Visual Studio, CodeBlocks, Jupyter Notebooks, ChatGPT, Cursor IDE

"""

job_description = """Experience
2 years to less than 3 years

Responsibilities
Tasks
Consult with clients to develop and document Website requirements
Communicate technical problems, processes and solutions
Prepare reports, manuals and other documentation on the status, operation and maintenance of software
Assist in the collection and documentation of user's requirements
Create and optimize content for Website using a variety of graphics, database, animation and other software
Assist in the development of logical and physical specifications
Lead and co-ordinate multidisciplinary teams to develop Website graphics, content, capacity and interactivity
Conduct tests and perform security and quality controls
Plan, design, write, modify, integrate and test Web-site related code"""

# Paths to the LaTeX template files
start_template_path = os.path.join(os.path.dirname(__file__), 'latex_resume_format_start.tex')
end_template_path = os.path.join(os.path.dirname(__file__), 'latex_resume_format_end.tex')

with open(start_template_path, 'r') as file:
    start_template = file.read()

with open(end_template_path, 'r') as file:
    end_template = file.read()

def create_latex_resume_assistant():
    client = openai.Client()
    assistant = client.beta.assistants.create(
        model="gpt-4-1106-preview",
        name="LaTeX Resume Content Integrator",
        instructions="""Integrate the user's resume details into the 'latex_end_template', adhering strictly to its structure and format.
        Start from \begin{document}, and ensure the content aligns with the provided LaTeX commands and sections.
        Focus on the Experience, Education, Projects, and Technical Skills sections, using the user's resume information.
        Avoid any unicode characters and extra LaTeX commands not present in the template.
        If specific data (like project dates) are absent in the user's resume, omit those elements from the template. Highlight in bold any resume content that matches key terms in the job description,
        particularly in the Experience and Projects sections. Tailor the resume to emphasize aspects relevant to the job description, without adding information not present in the user's resume.
        The output should form a one-page, fully formatted LaTeX document, ready to merge into a complete resume. also dont write ```latex at the start and ``` at the end""",
        tools=[]
    )
    return assistant

def generate_latex_resume_from_input(user_resume, job_description, latex_end_template, assistant_id):
    client = openai.Client()
    print("Creating a thread for conversation...")
    thread = client.beta.threads.create()
    thread_id = thread.id

    print("Adding messages to the thread...")
    messages = [
        {"role": "user", "content": user_resume},
        {"role": "user", "content": job_description},
        {"role": "user", "content": latex_end_template}
    ]
    for message in messages:
        client.beta.threads.messages.create(thread_id=thread_id, role=message["role"], content=message["content"])

    print("Running the assistant with the created thread...")
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    while run.status in ['queued', 'in_progress']:
        print(f"Waiting for run to complete... Status: {run.status}")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    if run.status == 'completed':
        print("Run completed. Fetching messages...")
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for message in messages.data:
            if message.role == "assistant":
                print("Assistant message found. Checking for LaTeX content...")
                for part in message.content:
                    if isinstance(part, openai.types.beta.threads.message_content_text.MessageContentText):
                        print("MessageContentText object found.")
                        response_text = part.text.value
                        # Print the entire response text
                        print("Generated LaTeX content:")
                        print(response_text)
                        return response_text
                print("No valid LaTeX content found in MessageContentText object.")
    else:
        print(f"Run did not complete successfully. Status: {run.status}")
    return None

def combine_and_save_latex_resume(start_content, generated_content):
    combined_content = start_content + '\n' + generated_content
    output_file_path = os.path.join(os.path.dirname(__file__), 'generated_resume.tex')
    with open(output_file_path, 'w') as output_file:
        output_file.write(combined_content)
    return f"LaTeX resume saved to {output_file_path}"

latex_resume_assistant = create_latex_resume_assistant()
generated_latex_content = generate_latex_resume_from_input(user_resume_text, job_description, end_template, latex_resume_assistant.id)

# Combine start template content with generated content and save
result = combine_and_save_latex_resume(start_template, generated_latex_content)
print(result)
