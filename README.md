# Project Overview

## Introduction
This project is a web scraper built using **Playwright** and Python. The scraper automates logging into a user portal, extracting structured account data (e.g., addresses, balances, usage history), downloading associated statements and bills, and storing the information in a JSON file for further use.

---

## Features
1. **Automated Login**: 
   - Logs into the user portal using credentials and a two-factor authentication (MFA) code.
   - Verifies successful login by checking the page content.

2. **Data Extraction**: 
   - Extracts account information (e.g., address, account number, due date, current balance, last month's usage) from structured HTML elements.
   - Handles pagination to collect data across multiple pages.

3. **Data Storage**: 
   - Saves extracted data in a structured JSON format, omitting sensitive or unnecessary fields (e.g., `latest_bill_link`).

4. **File Downloads**:
   - Automates downloading the latest bills and all recent statements for each account.
   - Ensures downloaded files are uniquely named and labeled for organization.

---

## Code Structure
The project is designed with modularity in mind, making it easy to extend and maintain:

### **1. `scraper.py`**
   - Contains the core functionality of the scraper, including methods for:
     - Browser and session management (e.g., starting/stopping the browser).
     - Logging into the portal.
     - Extracting account data and saving it as JSON.
     - Downloading bills and statements across multiple pages.

### **2. `config.py`**
   - Centralizes configuration settings, such as the `BASE_URL`, login credentials, MFA code, and timeout values.
   - Uses environment variables for sensitive information (e.g., `USERNAME`, `PASSWORD`), providing flexibility and security.
   - Validates required environment variables, raising clear errors if any are missing.

### **3. `tests/test_scraper.py`**
   - Comprehensive test suite built with **pytest** to validate all functionalities of the scraper.
   - Test cases ensure:
     - Successful login to the portal.
     - Accurate data extraction for account cards.
     - Proper JSON file creation with the correct structure.
     - Successful downloading of files, with validations for file existence.
     - Pagination handling for downloading statements across multiple pages.

