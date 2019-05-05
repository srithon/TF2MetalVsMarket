# Refresh metal prices

from selenium import webdriver

from time import sleep

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from mysql.connector.errors import IntegrityError

connection = mysql.connector.connect(host='localhost',
                             database='tf2metalvsmarketprice',
                             user='root',
                             password='LrD3FZGUz5JXy5c')

cursor = connection.cursor(buffered=True)

                                # replaced Unique with blank
rarity_index_map = ['Genuine ', 'Vintage ', '', 'Strange ', 'Haunted ', 'Collector\'s ']

ref_per_key = 46.55
ref_per_random_craft_hat = 1.28


def find_elem(item, selector):
    return item.find_element_by_css_selector(selector)


def process_row(item_row):
    global rarity_index_map, ref_per_key, ref_per_random_craft_hat, cursor
    
    base_name = find_elem(item_row, 'td:nth-child(1)').text
    base_type = find_elem(item_row, 'td:nth-child(2)').text
    
    for i in range(3, 9):
        current_field = find_elem(item_row, 'td:nth-child({})'.format(i)).text
        if current_field != '':
            price = current_field[:current_field.find(' ')]
            
            dash_ind = price.find('–')
            
            if dash_ind != -1:
                price_low = price[:dash_ind]
                price_high = price[(dash_ind + 1):]
                price = (float(price_low) + float(price_high)) / 2.0
            else:
                price = float(price)
            
            if 'key' in current_field:
                price *= ref_per_key
            elif 'hat' in current_field:
                price *= ref_per_random_craft_hat

            name = rarity_index_map[i - 3] + base_name
            query = """UPDATE `tf2 metal vs steam market prices`
                    (name, type, metalPrice, metalPriceTimeUpdated) SET
                    (%s, %s, %s, now())"""
            # print(query % (name, base_type, price))
            try:
                cursor.execute(query, (name, base_type, price))
            except IntegrityError as e:
                print(e)


def save():
    global connection
    connection.commit()


def close_db():
    global cursor, connection
    
    if(connection.is_connected()):
            connection.commit()
            connection.close()
            cursor.close()
            print('Committed and closed')


def main():
    firefox_profile = webdriver.FirefoxProfile()
    
    """firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # Disable images
    firefox_profile.set_preference('permissions.default.image', 2)
    # Disable Flash
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                   'false')
    firefox_profile.set_preference('javascript.enabled', True)#False)"""
    
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    
    driver.get('https://backpack.tf/spreadsheet')
    
    items_body = driver.find_element_by_css_selector('#pricelist > tbody:nth-child(2)')
    items = items_body.find_elements_by_tag_name('tr')
    
    print(len(items))
    
    try:
        for i, item_row in enumerate(items):
            process_row(item_row)
            
            if i % 100 == 0:
                save()
    finally:
        close_db()
        driver.quit()
    
main()  
    