# Refresh metal prices

from selenium import webdriver

from time import sleep


def main():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # Disable images
    firefox_profile.set_preference('permissions.default.image', 2)
    # Disable Flash
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                   'false')
    firefox_profile.set_preference('javascript.enabled', False)
    
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    
    driver.get('https://backpack.tf/pricelist')
    
    sleep(5)
    
    driver.execute_script('updatePaging({['data-paging']: "4536"});')
    
    sleep(10)
    
    items_container = driver.find_element_by_css_selector('#pricelistContainer')
    
    items = items_container.find_elements_by_tag_name('li')
    
    for i in range(30):
        item = items[i]
        
        data = item.find_element_by_xpath('./li/div/a/span')
        content = data.get_attribute('data-content')
        name = data.get_attribute('data-original-title')
        
        sub_string = content[(content.find('or') + 3):]
        
        split_point = sub_string.find(' ref')
        ref_price = sub_string[:split_point]
        real_price = sub_string[(split_point + 6):]
        
        print( (name, ref_price, real_price) )
    
    driver.quit()
    
main()  
    