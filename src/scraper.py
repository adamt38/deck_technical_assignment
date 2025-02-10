import os
import time
import json
from playwright.sync_api import sync_playwright
from .config import BASE_URL, USERNAME, PASSWORD, TIMEOUT, MFA_CODE


class Scraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    def start_browser(self, headless=True):
        """Starts the browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()

    # ------ Navigating and Logging In ----------

    def navigate_to_login(self):
        """Navigates to the main page, clicks the login button, and accepts cookies."""
        print("Navigating to the main page...")
        self.page.goto(BASE_URL, timeout=TIMEOUT * 1000)

        # Click the "Try 2FA Login" button
        print("Clicking the 'Try 2FA Login' button...")
        self.page.click("a:has-text('Try 2FA Login')")  
        self.page.wait_for_load_state("networkidle")  

        # Accept cookies
        print("Clicking 'Allow all cookies' button...")
        self.page.click("button.btn-allow")  

        print("Cookies accepted. Ready to proceed.")

    def perform_login(self):
        """Fills the login form, enters the MFA code, and submits it."""
        print("Filling in the username...")
        self.page.fill("input[name='username']", USERNAME)

        print("Filling in the password...")
        self.page.fill("input[name='password']", PASSWORD)

        print("Submitting the login form...")
        self.page.click("button[type='submit']")

        # Wait for the MFA input field to appear
        print("Waiting for the MFA code input field...")
        self.page.wait_for_selector("input#mfa_code") 

        print("Filling in the MFA code...")
        self.page.fill("input#mfa_code", MFA_CODE)  

        print("Submitting the MFA code...")
        self.page.click("button[type='submit']")  

        print("Waiting for post-login content...")
        self.page.wait_for_selector("h2:has-text('PowerCo Dashboard')", timeout=60000)  # Wait for dashboard header

    def get_page_title(self):
        """Gets the current page title."""
        return self.page.title()
    
    def login_to_website(self, headless=True):
        """Performs the full login process."""
        self.start_browser(headless=headless)
        self.navigate_to_login()
        self.perform_login()
        title = self.get_page_title()
        return title

    # -------- Data extraction and data extraction helper methods ----------
    def extract_text_from_card(self, card, selector, label):
        """Safely extracts text from a specific element within a card."""
        try:

            card.locator(selector).wait_for(timeout=5000)  
            return card.locator(selector).inner_text().split(":")[1].strip()
        except Exception:
            raise ValueError(f"{label} not found in card.")
        
    def extract_account_cards(self):
        """Extracts data from all account cards using XPath."""
        print("Extracting account cards using XPath...")

        try:
            self.page.wait_for_selector("xpath=//div[contains(@class, 'grid') and contains(@class, 'gap-6') and contains(@class, 'mb-8')]", timeout=30000)
        except Exception as e:
            print("Error: Account cards container did not load within the timeout period.")
            raise e

        # Locate all account cards within the container using XPath
        account_cards = self.page.locator("xpath=//div[contains(@class, 'grid') and contains(@class, 'gap-6') and contains(@class, 'mb-8')]/div[contains(@class, 'bg-white')]").all()

        if len(account_cards) == 0:
            print("No account cards found.")
            return []

        print(f"Found {len(account_cards)} account card(s). Processing...")

        accounts = []

        for i, card in enumerate(account_cards, start=1):
            try:
                print(f"Processing card {i}...")

                # Extract data using XPath
                address = card.locator("xpath=.//h3[contains(@class, 'text-xl') and contains(@class, 'font-semibold')]").inner_text().strip()
                account_number = card.locator("xpath=.//p[contains(text(), 'Account #:')]").inner_text().split(":")[1].strip()
                current_balance = card.locator("xpath=.//span[contains(@class, 'font-semibold') and contains(text(), '$')]").inner_text().strip()
                due_date = card.locator("xpath=.//span[contains(text(), ', 202')]").inner_text().strip()
                last_month_usage = card.locator("xpath=.//span[contains(text(), 'kWh')]").inner_text().strip()
                latest_bill_link = card.locator("xpath=.//a[contains(@class, 'bg-blue-600') and contains(@class, 'hover:bg-blue-700')]").get_attribute("href")

                # Append extracted data to accounts list
                accounts.append({
                    "address": address,
                    "account_number": account_number,
                    "current_balance": current_balance,
                    "due_date": due_date,
                    "last_month_usage": last_month_usage,
                    "latest_bill_link": latest_bill_link,
                })

                print(f"Card {i} processed successfully.")

            except Exception as e:
                print(f"Error extracting data from card {i}: {e}")

        print(f"Accounts extracted: {len(accounts)}")
        
        return accounts
    

    # -------- Writing extracted data from cards to JSON ----------
    def write_accounts_to_json(self, accounts, filename="extracted_accounts.json"):
        """
        Writes account card data to a JSON file, excluding the 'latest_bill_link' field.
        """
        directory = os.getcwd()  # Use the current working directory
        filepath = os.path.join(directory, filename)  # Combine directory and filename

        try:
            sanitized_accounts = [
                {key: value for key, value in account.items() if key != "latest_bill_link"}
                for account in accounts
            ]

            with open(filepath, "w") as json_file:
                json.dump(sanitized_accounts, json_file, indent=4)
                
            print(f"Account data successfully written to {filepath}.")
        except Exception as e:
            print(f"Error writing account data to JSON: {e}")


    # ------- Downloading Latest Bills -------- # 

    def download_latest_bills_from_cards(self, accounts):
        """
        Downloads the latest bills for the specific accounts extracted from the cards.
        """
        print("Downloading latest bills for extracted cards...")
        for i, account in enumerate(accounts):
            try:
                # Locate the specific card by its address or account number
                card_xpath = f"//h3[contains(text(), '{account['address']}')]/ancestor::div[contains(@class, 'bg-white')]"
                card = self.page.locator(card_xpath)

                # Trigger the download for "Latest Bill"
                with self.page.expect_download() as download_info:
                    card.locator("a:has-text('Latest Bill')").click()
                download = download_info.value
                file_name = f"{account['address'].replace(' ', '_')}_latest_bill_{i + 1}.pdf"
                download.save_as(file_name)
                print(f"Downloaded bill for account: {account['account_number']}, file: {file_name}")
            except Exception as e:
                print(f"Error downloading bill for account: {account['account_number']}. Error: {e}")


    # -------- Downloading all recent statments -----------

    def download_statements_across_pages(self):
        """
        Downloads all statements across multiple pages, labeling files sequentially.
        """
        try:
            file_counter = 1  
            page_number = 1

            while True:
                print(f"Downloading statements on page {page_number}...")
                file_counter = self.download_all_statements(file_counter)

                # Check if the "Next" button exists and is enabled
                next_button = self.page.locator("//a[contains(text(), 'Next')]")
                if not next_button.is_visible():
                    print("No 'Next' button found. Exiting pagination.")
                    break

                # Click the "Next" button to go to the next page
                print("Navigating to the next page...")
                next_button.click()
                self.page.wait_for_load_state("networkidle")  
                page_number += 1

        except Exception as e:
            print(f"Error during pagination and download: {e}")

    def download_all_statements(self, start_index=1):
        """
        Downloads all statements from the current page and numbers the files starting from the given index.
        """
        try:
            # Locate all download links in the table
            statement_links = self.page.locator("//tr/td/a[contains(@class, 'text-blue-600')]").all()
            print(f"Found {len(statement_links)} statements to download.")

            for i, link in enumerate(statement_links, start=start_index):
                try:

                    with self.page.expect_download() as download_info:
                        link.click()
                    download = download_info.value
                    download.save_as(f"statement_{i}.pdf")
                    print(f"Downloaded statement: statement_{i}.pdf")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error downloading statement {i}: {e}")

            return start_index + len(statement_links)

        except Exception as e:
            print(f"Error downloading statements on the current page: {e}")
            return start_index

    # ------ Saving to JSON ------

    def save_to_json(self, data, filename="accounts_data.json"):
        """Saves extracted account data to a JSON file."""
        try:
            with open(filename, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data saved successfully to {filename}.")
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")

    # # ----- Logging and and extracting data all together ----- 

    # def login_and_extract_data(self, headless=True):
    #     """Performs the full login, data extraction, and download process."""
    #     try:
    #         self.start_browser(headless=headless)
    #         self.navigate_to_login()
    #         self.perform_login()

    #         accounts = self.extract_account_cards()
    #         self.save_to_json(accounts, "accounts_data.json")

    #         # Download latest bills
    #         self.download_latest_bills()

    #         # Return page title
    #         return self.page.title()
    #     finally:
    #         self.close_browser()

     # ------ Closing the browser once we are done ------# 
    
    def close_browser(self):
        """Safely closes the browser and cleans up."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Error while closing the browser: {e}")




