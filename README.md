# Appl.ai: Your AI-Powered Job Application Assistant

Appl.ai is a web application designed to streamline and automate the job application process through the power of artificial intelligence and web scraping. It helps users save time and effort while maximizing their chances of landing their desired positions by automating various steps of the application process, from job discovery to the submission of applications.

## Badges

![React](https://img.shields.io/badge/React-16.8+-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Flask](https://img.shields.io/badge/Flask-1.x-orange)
![LaTeX](https://img.shields.io/badge/LaTeX-Editor-green)
![OpenAI GPT-4](https://img.shields.io/badge/OpenAI%20GPT--4-Enabled-red)
![Selenium WebDriver](https://img.shields.io/badge/Selenium-WebDriver-critical)
![MIT License](https://img.shields.io/badge/license-MIT-green)


## Functionality Overview

### Job Discovery
- **Resume Analysis**: Upload your resume in PDF format. Appl.ai uses OpenAI's language models to analyze your skills and experience, creating a comprehensive understanding of your qualifications.
- **Targeted Job Search**: Constructs a search query based on your resume analysis for the Canadian Job Bank website and scrapes relevant job postings.
- **Detailed Job Listings**: Provides key information such as company name, position, salary range, location, and a direct link to the job posting.

### Tailored Resume and Cover Letter Generation
- **AI-Powered Customization**: Generates personalized resumes and cover letters tailored to each job posting using OpenAI's GPT-4 model.
- **Professional Formatting**: Uses LaTeX to ensure that the documents are beautifully formatted and professional.
- **Keyword Optimization**: Highlights relevant keywords from the job description within your resume and cover letter.
- **Seamless Overleaf Integration**: Allows for easy editing and customization of the generated documents via Overleaf.

### Effortless Email Drafting
- **Personalized Email Generation**: Crafts professional email drafts for your applications.
- **Targeted Content**: Focuses on highlighting your relevant skills, experiences, and enthusiasm for the position.

### User-Friendly Interface
- **Simple and Intuitive**: Easy-to-use interface for all functionalities, from uploading resumes to browsing job listings.
- **Email Preview**: Allows you to review the generated email body before sending.

## Technical Implementation

- **Frontend**: Developed with React and Reactstrap for a responsive user interface.
- **Backend**: Uses Python and Flask for server-side operations.
- **AI & NLP**: Leverages OpenAI's GPT-4 and GPT-3.5 for text analysis and generation.
- **PDF Processing**: Utilizes the PyPDF2 library for extracting text from uploaded resumes.
- **Web Scraping**: Employs Selenium WebDriver for automated web interactions.
- **Document Formatting**: Managed through LaTeX for professional document presentation.
- **LaTeX Editor Integration**: Integrated with Overleaf for document editing.

## Project Status and Future Development

Appl.ai is under active development with plans to:
- **Expand Job Sources**: Integrate with more job boards.
- **Application Tracking System**: Track the status of submitted applications.
- **User Profile Management**: Enable storage of application history and preferences.
- **Direct Application Submission**: Integrate with email sending APIs.
- **Multilingual Support**: Expand language support to facilitate job searches globally.

## Contributing

Contributions are welcome! Please refer to `CONTRIBUTING.md` for guidelines on how to contribute to Appl.ai. Let's work together to enhance this tool for job seekers everywhere.

## Disclaimer

Appl.ai is a tool intended to assist with the job application process. While we strive for accuracy, we cannot guarantee job application success. Users are encouraged to review and personalize the generated documents.


