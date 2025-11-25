import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def get_team_file_prefixes(team_name):
    return {
        "team_5": {
            "input_suffix": "_team2.json",
            "output_suffix": "_team5.json"
        }
    }.get(team_name)

def perform_google_search(query, driver):
    driver.get(f"https://www.google.com/search?q={query}")
    time.sleep(2)  # Give time to load

    links = []
    results = driver.find_elements(By.XPATH, '//div[@class="tF2Cxc"]/div/div/div/a')
    for res in results:
        href = res.get_attribute("href")
        if "linkedin.com/in/" in href:
            links.append(href)
    return links

def process_file_team5(input_path, driver):
    with open(input_path, "r") as infile:
        people = json.load(infile)

    results = []

    for person in people:
        name = person.get("name")
        email = person.get("email")
        company = person.get("company_name")

        if not name or not email:
            continue

        query = f'site:linkedin.com/in/ "{name}" "{company}"'
        matches = perform_google_search(query, driver)

        if matches:
            results.append({
                "name": name,
                "email": email,
                "company_name": company,
                "linkedin_url": matches[0]  # first match only
            })

    return results

def main():
    base_dir = "country"
    team_name = "team_5"
    prefixes = get_team_file_prefixes(team_name)

    # Setup Selenium (Chrome headless)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(prefixes["input_suffix"]):
                continue

            input_path = os.path.join(root, file)
            output_path = os.path.join(root, file.replace(prefixes["input_suffix"], prefixes["output_suffix"]))

            print(f"🔍 Searching LinkedIn for entries in: {input_path}")
            result = process_file_team5(input_path, driver)

            with open(output_path, "w") as outfile:
                json.dump(result, outfile, indent=2)

            print(f"✅ Saved LinkedIn results to: {output_path}")

    driver.quit()

if __name__ == "__main__":
    main()
