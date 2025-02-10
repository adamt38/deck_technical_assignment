import json
from src.scraper import Scraper
import os

def test_login_to_dashboard():
    """Tests if the scraper successfully logs into the dashboard."""
    scraper = Scraper()
    try:
        # Perform the login
        page_title = scraper.login_to_website(headless=True)
        
        assert "PowerCo - Customer Dashboard" in page_title, \
            f"Expected 'PowerCo - Customer Dashboard' but got '{page_title}'"
    finally:
        scraper.close_browser()

def test_extract_account_cards():
    """Tests if account cards within the grid container are correctly extracted."""
    scraper = Scraper()
    try:
        scraper.start_browser(headless=True)
        scraper.navigate_to_login()
        scraper.perform_login()

        accounts = scraper.extract_account_cards()
        assert len(accounts) == 2, f"Expected 2 account cards, but extracted {len(accounts)}."
        
        expected_addresses = ["123 Main Street", "456 Oak Avenue"]
        expected_account_numbers = ["1234-5678", "8765-4321"]

        for i, account in enumerate(accounts):
            assert account["address"] == expected_addresses[i], f"Address mismatch for card {i + 1}"
            assert account["account_number"] == expected_account_numbers[i], f"Account number mismatch for card {i + 1}"
            assert "current_balance" in account, f"Current balance missing for card {i + 1}"
            assert "due_date" in account, f"Due date missing for card {i + 1}"
            assert "last_month_usage" in account, f"Last month usage missing for card {i + 1}"
            assert "latest_bill_link" in account, f"Latest bill link missing for card {i + 1}"

        print("Test passed: All account cards extracted successfully.")
    finally:
        scraper.close_browser()

def test_download_latest_bills_from_cards():
    """
    Tests downloading latest bills for the extracted cards.
    """
    scraper = Scraper()

    try:
        scraper.start_browser(headless=True)
        scraper.navigate_to_login()
        scraper.perform_login()

        accounts = scraper.extract_account_cards()
        assert len(accounts) > 0, "No account cards found!"
        scraper.download_latest_bills_from_cards(accounts)

        # Verify that files were downloaded (based on naming convention)
        for i, account in enumerate(accounts):
            file_name = f"{account['address'].replace(' ', '_')}_latest_bill_{i + 1}.pdf"
            file_path = os.path.join(os.getcwd(), file_name)
            assert os.path.exists(file_path), f"File {file_name} not found!"

        print("All bills downloaded successfully.")
    finally:
        scraper.close_browser()


def test_download_all_statements():
    """
    Tests downloading all statements from the table.
    """
    scraper = Scraper()
    try:
        scraper.start_browser(headless=True)
        scraper.navigate_to_login()
        scraper.perform_login()

        scraper.download_all_statements()

            # Verify downloaded files
        for i in range(1, 20):  
            file_path = f"statement_{i}.pdf"
            assert os.path.exists(file_path), f"File not downloaded: {file_path}"

    finally:
        scraper.close_browser()

def test_json_file_creation_without_bill_link():
    """
    Test to ensure the JSON file is correctly created without the 'latest_bill_link' field.
    """
    scraper = Scraper()
    try:
        scraper.start_browser(headless=True)
        scraper.navigate_to_login()
        scraper.perform_login()

        # Extract account cards
        accounts = scraper.extract_account_cards()
        assert len(accounts) > 0, "No account cards found!"

        json_file = "extracted_accounts.json"
        scraper.write_accounts_to_json(accounts, filename=json_file)
        assert os.path.exists(json_file), f"JSON file {json_file} not found!"
        print(f"File successfully saved at: {json_file}")


        # Validate the content of the JSON file
        with open(json_file, "r") as f:
            data = json.load(f)

            assert isinstance(data, list), "JSON data should be a list!"
            assert len(data) == len(accounts), "Mismatch in number of accounts and JSON data!"

            for account in data:
                assert "address" in account, "Missing 'address' field in JSON!"
                assert "account_number" in account, "Missing 'account_number' field in JSON!"
                assert "current_balance" in account, "Missing 'current_balance' field in JSON!"
                assert "due_date" in account, "Missing 'due_date' field in JSON!"
                assert "last_month_usage" in account, "Missing 'last_month_usage' field in JSON!"
                assert "latest_bill_link" not in account, "'latest_bill_link' should not be in JSON!"

            print(f"JSON file {json_file} is valid and does not contain 'latest_bill_link'.")
    finally:
        scraper.close_browser()

def test_download_statements_across_multiple_pages():
    """
    Tests downloading all statements across multiple pages.
    """
    scraper = Scraper()

    try:
        scraper.start_browser(headless=True)
        scraper.navigate_to_login()
        scraper.perform_login()

        # Download all statements across pages
        scraper.download_statements_across_pages()

        statement_files = [f"statement_{i}.pdf" for i in range(1, 40)]  
        missing_files = []

        for file_path in statement_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        assert not missing_files, f"The following files were not downloaded: {missing_files}"
        print("Test passed: All statements downloaded successfully across multiple pages.")
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        raise
    finally:
        scraper.close_browser()




