import time
import concurrent.futures 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from concurrent.futures import ThreadPoolExecutor

def click_show_more_jobs(driver):
    try:
        for _ in range(3):
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'moreresultbutton')))
            show_more_button = driver.find_element(By.ID, 'moreresultbutton')
            show_more_button.click()
            time.sleep(2)
    except (NoSuchElementException, TimeoutException):
        print("Show more jobs button not found, not clickable, or no more jobs to load.")
    except Exception as e:
        print(f"An error occurred while clicking the button: {e}")

def scrape_job_bank_links(driver, url):
    job_links = []
    try:
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
        email = email_element.text

        # Scrape the job description and remove newline characters
        job_description_element = driver.find_element(By.CSS_SELECTOR, "div.job-posting-detail-requirements")
        job_description = job_description_element.text.replace('\n', ' ')

        return {job_link: {'job_email': email, 'job_description': job_description}}
    except Exception as e:
        print(f"Error processing {job_link}: {str(e)}")
        return {job_link: {'job_email': None, 'job_description': None}}
    finally:
        if driver:
            driver.quit()


def scrape_emails_in_parallel(job_links):
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_link = {executor.submit(process_job_link, link): link for link in job_links}
        for future in concurrent.futures.as_completed(future_to_link):
            result = future.result()
            results.update(result)
    return results

if __name__ == "__main__":
    driver = webdriver.Chrome()

    job_bank_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?d=50&fage=2&fcid=5169&fcid=12083&fcid=296553&fcid=296554&fn21=21230&fn21=21232&fn21=21234&fn21=94153&mid=22437&term=developer&sort=M"
    job_links = scrape_job_bank_links(driver, job_bank_url)
    driver.quit()

    email_results = scrape_emails_in_parallel(job_links)
    print(email_results)
