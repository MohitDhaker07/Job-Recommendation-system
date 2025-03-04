import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def scrape_foundit_jobs(search_query: str):
    """
    Given a job search query (e.g., 'Python Developer'),
    this function uses Selenium to scrape results from foundit.in
    and returns a list of (Job Title, Company, Location) tuples.
    """
    
    # Configure Chrome options
    options = webdriver.ChromeOptions()
    # Uncomment the next line if you'd like to run in headless mode:
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors=yes")

    # Set capabilities
    options.set_capability("acceptInsecureCerts", True)
    options.set_capability("goog:loggingPrefs", {'browser': 'ALL'})

    driver = webdriver.Chrome(options=options)

    results = []

    try:
        driver.get("https://www.foundit.in/")
        
        # Wait for the div to be clickable
        div_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "heroSectionDesktop-skillsAutoComplete"))
        )
        # Click the div
        try:
            div_element.click()
        except:
            driver.execute_script("arguments[0].click();", div_element)

        # Wait for the input to be clickable
        input_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "heroSectionDesktop-skillsAutoComplete--input"))
        )
        # Click the input
        try:
            input_element.click()
        except:
            driver.execute_script("arguments[0].click();", input_element)

        # Enter search query and press Enter
        input_element.send_keys(search_query)
        input_element.send_keys(Keys.ENTER)

        # Give time for results page to load
        time.sleep(5)

        # Locate the elements
        job_titles = driver.find_elements(By.CLASS_NAME, "jobTitle")
        company_names = driver.find_elements(By.CLASS_NAME, "companyName")
        locations = driver.find_elements(By.CSS_SELECTOR, ".details.location")

        count = min(len(job_titles), len(company_names), len(locations))

        for i in range(count):
            title_text = job_titles[i].text.strip()
            company_text = company_names[i].text.strip()
            location_text = locations[i].text.strip()
            results.append((title_text, company_text, location_text))

    except Exception as e:
        st.error(f"An error occurred during scraping: {e}")
    finally:
        driver.quit()

    return results

def main():
    # Basic page config
    st.set_page_config(
        page_title="Job Search App",
        layout="centered",
    )

    # Include Font Awesome for icons
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        """,
        unsafe_allow_html=True
    )
    
    # Custom CSS for a nicer look
    st.markdown(
        """
        <style>
        /* Set a light-blue background for the entire page */
        body {
            background-color: #CCB0AA !important;
        }

        /* Center the main container */
        .main > div {
            max-width: 800px;
            margin: 0 auto;
        }

        /* Style the title */
        h1 {
            text-align: center;
            margin-bottom: 1rem;
        }

        /* Make the text input (search bar) bigger */
        /* Force a taller height and bigger font */
        input[type="text"] {
            height: 3rem !important;
            font-size: 1.2rem !important;
        }
        
        /* Make each job card pop */
        .job-card {
            background-color: #FFFFFF;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .job-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
        }
        
        .job-title i {
            margin-right: 8px;
        }

        .job-company, .job-location {
            margin: 0.2rem 0;
            display: flex;
            align-items: center;
        }

        .job-company i,
        .job-location i {
            margin-right: 6px;
        }
        </style>
        
        """,
        unsafe_allow_html=True
    )

    # App title
    st.title("Job Recommendation System")

    # Search bar (with bigger size)
    search_query = st.text_input("Job Recommendation System", "")

    # Button to trigger scraping
    if st.button("Search"):
        if search_query.strip() == "":
            st.warning("Please enter a valid search query.")
        else:
            with st.spinner("Looking for the best job for you..."):
                results = scrape_foundit_jobs(search_query)

            if results:
                st.success(f"Found {len(results)} jobs for '{search_query}'!")
                
                # Display each job as a card with icons
                for (title, company, location) in results:
                    st.markdown(
                        f"""
                        <div class="job-card">
                            <div class="job-title">
                                <i class="fa fa-briefcase"></i> {title}
                            </div>
                            <p class="job-company">
                                <i class="fa fa-building"></i> {company}
                            </p>
                            <p class="job-location">
                                <i class="fa fa-map-marker"></i> {location}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No results found, or there was an issue loading the results.")

if __name__ == "__main__":
    main()
