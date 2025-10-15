import re
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # 1. Log in as a staff user
    page.goto("http://localhost:8000/users/login/")

    # Add an explicit wait for the form to be ready
    page.wait_for_selector("form.login-form")

    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()

    # Wait for navigation to the dashboard, confirming login was successful
    expect(page).to_have_url(re.compile(".*admin_dashboard.*"))
    print("Login successful.")

    # 2. Navigate to the branding customization page
    page.get_by_role("link", name="Customize").click()
    expect(page).to_have_url(re.compile(".*edit_branding.*"))
    print("Navigated to customization page.")

    # 3. Take a screenshot of the form before changes
    page.screenshot(path="jules-scratch/verification/01_before_changes.png")
    print("Screenshot of original form taken.")

    # 4. Fill out the form with new branding information
    new_name = "Jules' Cafe"
    new_slogan = "The best coffee in town!"
    new_primary_color = "#3498db"  # A nice blue
    new_secondary_color = "#f1c40f" # A nice yellow

    page.get_by_label("Name").fill(new_name)
    page.get_by_label("Slogan").fill(new_slogan)

    page.locator('input[name="primary_color"]').fill(new_primary_color)
    page.locator('input[name="secondary_color"]').fill(new_secondary_color)

    # Upload a logo (we'll create a dummy file for this)
    with open("jules-scratch/verification/test_logo.png", "wb") as f:
        f.write(b"dummy image data")
    page.get_by_label("Logo").set_input_files("jules-scratch/verification/test_logo.png")

    print("Form filled out with new branding.")

    # 5. Submit the form
    page.get_by_role("button", name="Save Changes").click()

    # Wait for the success message to ensure the form was processed
    expect(page.get_by_text("Branding updated successfully!")).to_be_visible()
    print("Branding form submitted successfully.")

    # 6. Navigate to the home page and verify changes
    page.goto("http://localhost:8000/")

    # Check for the new name and slogan
    expect(page.get_by_text(new_name)).to_be_visible()
    expect(page.get_by_text(new_slogan)).to_be_visible()

    expect(page.locator(f'img[src*="test_logo"]')).to_be_visible()
    print("Name, slogan, and logo verified on home page.")

    # Take a screenshot of the home page with new branding
    page.screenshot(path="jules-scratch/verification/02_after_changes_homepage.png")
    print("Screenshot of updated home page taken.")

    # 7. Navigate to the admin dashboard and verify changes
    page.goto("http://localhost:8000/admin_dashboard/")
    expect(page.get_by_text(new_name)).to_be_visible()
    print("Name verified on admin dashboard.")

    # Take a screenshot of the admin dashboard
    page.screenshot(path="jules-scratch/verification/03_after_changes_dashboard.png")
    print("Screenshot of updated admin dashboard taken.")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
