from playwright.sync_api import sync_playwright
import sqlite3
import os
import requests

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "test.db")

def cleanup_user(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
    except sqlite3.OperationalError:
        print("Database not ready or table does not exist.")
    finally:
        conn.close()
    
def test_signup_and_login():
    test_username = "testuser123"
    test_password = "pass123"

    # Clean up the user if it already exists
    cleanup_user(test_username)

    # Signup via API
    signup_response = requests.post(
        "http://localhost:8000/signup",
        json={"username": test_username, "password": test_password}
    )
    assert signup_response.status_code == 200, f"API signup failed: {signup_response.text}"

    # Login via API
    login_response = requests.post(
        "http://localhost:8000/login",
        json={"username": test_username, "password": test_password}
    )
    assert login_response.status_code == 200, f"API login failed: {login_response.text}"
    token = login_response.json().get("access_token")
    assert token, "No access token received"

    # E2E test with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("http://localhost:5173")

        page.click("text=Login")
        page.fill('input[placeholder="Username"]', test_username)
        page.fill('input[placeholder="Password"]', test_password)
        page.click('button:has-text("Login")')

        page.wait_for_selector(f"text=Welcome, {test_username}", timeout=5000)
        assert page.is_visible(f"text=Welcome, {test_username}"), "Login failed or welcome message not found"    

        browser.close()
