from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://yourwebsite.com")

buttons = driver.find_elements("tag name", "button")

for button in buttons:
    print("Button Text:", button.text)
    print("Button Color:", button.value_of_css_property("background-color"))

driver.quit()
