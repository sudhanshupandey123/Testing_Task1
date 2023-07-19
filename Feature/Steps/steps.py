from behave import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time

parent_path = ''
actual_price = 0
total_num_of_prod = 0
index = []

Locators = {
    "INPUT_AREA": "//input[@id='twotabsearchtextbox']",
    "INPUT_CLICK": "//input[@id='nav-search-submit-button']",
    "RATING": "//*[@class='a-icon-alt']",
    "PRODUCT_LIST": '//*[@class="a-section aok-relative s-image-fixed-height"]',
    "PRICE": "//span[@class='a-price-whole']",
    "ADD_TO_CART": "//input[@id='add-to-cart-button']",
    "SUB_TOTAL": '//span[@id="attach-accessory-cart-subtotal"]'
}


@given('User is on Amazon Page')
def opening_page(context):
    """
    Just Opening Window And Passing Link To Reach at main page and maximizing the window


    """
    context.driver = webdriver.Chrome()
    context.driver.get("https://www.amazon.in/")
    context.driver.maximize_window()


@when(u'He Search For Product Name "{product}"')
def product_searching(context, product):
    """
    In This I Generated Location For Input tag so that we can pass value to that for element
    search

    :param product: Holding The Value Of Product For Search

    """
    wait = WebDriverWait(context.driver, 20)
    input_prod = wait.until(ec.presence_of_element_located((By.XPATH, Locators["INPUT_AREA"])))
    input_prod.send_keys(product)
    original_window = context.driver.current_window_handle
    wait.until(ec.presence_of_element_located((By.XPATH, Locators['INPUT_CLICK']))).click()
    parent_url = context.driver.current_window_handle
    global parent_path
    parent_path = parent_url


@when(u'He filters product based on more than "{rating}" star rating')
def filtering_product_based_on_rating(context, rating):
    """
    In This Based On the rating parameter i filtered the product having rating more than
    given rating parameter and storing their index position to index variable for further use
    :param rating: Value Based on which i am filtering product

    """
    wait = WebDriverWait(context.driver, 10)
    rank_list = wait.until(ec.presence_of_all_elements_located((By.XPATH, Locators['RATING'])))
    # rank_list = wait.until(ec.presence_of_all_elements_located((By.XPATH, "//*[@class='a-icon-alt']")))

    all_prod = wait.until(
        ec.presence_of_all_elements_located(
            (By.XPATH, Locators['PRODUCT_LIST'])))

    index_pos = []
    for i in range(len(rank_list)):
        if float(rank_list[i].get_attribute('textContent').split()[0]) >= float(rating):
            index_pos.append(i)
    global index
    index = index_pos


@when(u'He add first "{num_of_prod}" product to cart')
def add_to_cart(context, num_of_prod):
    """
    Based On The Rating Top Product Adding To Cart And Before that storing the actual price
    summation to a variable act_price so we can compare and end with summarized price
    :param num_of_prod: Store Total Number of product we want to cart

    """
    wait = WebDriverWait(context.driver, 10)
    price = wait.until(ec.presence_of_all_elements_located((By.XPATH, Locators['PRICE'])))
    all_prod = wait.until(
        ec.presence_of_all_elements_located((By.XPATH, Locators['PRODUCT_LIST'])))
    count = 1
    act_price = 0
    top_pro = 1
    for i in range(len(all_prod)):
        if i in index:
            print(float(price[i].get_attribute('textContent').replace(',', '')))
            act_price += float(price[i].get_attribute('textContent').replace(',', ''))
            time.sleep(10)
            top_pro += 1
        if top_pro > int(num_of_prod):
            break
    global actual_price
    actual_price = act_price

    for i in range(len(all_prod)):
        if i in index:
            all_prod[i].click()
            han = context.driver.window_handles
            count += 1
        if count > int(num_of_prod):
            break
    for window_handle in set(han):
        if window_handle != parent_path:
            context.driver.switch_to.window(window_handle)
            wait.until(ec.element_to_be_clickable((By.XPATH, Locators['ADD_TO_CART']))).click()
            time.sleep(5)


@then('the cart value should be sum of products')
def comparing_price(context):
    """
    Comparing The Actual Summation of Price of added product with the summarized price
    showing on the web page after adding all product
    """
    wait = WebDriverWait(context.driver, 10)
    try:
        summarized_price = wait.until(
            ec.presence_of_element_located((By.XPATH, Locators['SUB_TOTAL']))).get_attribute(
            "textContent")
        assert actual_price == summarized_price
    except AssertionError as msg:
        print('Summarized Price And Actual Price Are Not Same')
    context.driver.quit()
