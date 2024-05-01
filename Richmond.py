from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import util
import re


def get_detail_info(soup,count,data):
    info = {}
    # 定位到包含所有课程信息的 div
    grid_content_div = soup.find('div', class_='bm-grid-content k-grid k-widget')
    if not grid_content_div:
        print("Div with class 'bm-grid-content k-grid k-widget' not found.")
        return []

    # 在 div 中找到所有包含课程信息的 ul 元素
    ul_element = grid_content_div.find('ul', {'data-bind': 'foreach: services'})
    
    if not ul_element:
        print("No ul elements found with attribute 'data-bind' equal to 'foreach: services'.")
        return []
        
    # 找到 ul 元素中所有的 course-service 元素
    course_service_elements = ul_element.find_all('course-service', {'params': 'viewModel: $data'})
    # print(count)
    # 遍历每个 course-service 元素
    course_service_element=course_service_elements[count-1]
    
    div_element = course_service_element.find("div", {"data-bind": "visible: isExpanded"})
    course_events = div_element.find_all("course-event", {"params": "viewModel: $data"})
    # 循环遍历每个<course-event>元素
    for course_event in course_events:
        # 创建一个空的字典用于存储当前<course-event>元素的信息
        info = {}
        # 提取关键信息并存储到字典中
        
        price_container = course_event.find('div', class_='bm-group-item-link')
        
        if price_container:
            # 提取价格信息
            price_element = price_container.find('div', class_='anchor bm-course-price bm-course-details')
            price = price_element.text.strip() if price_element else None
            
            # 提取网站链接
            website_element = price_container.find('a', class_='bm-button bm-details-button')
            base_url = "https://richmondcity.perfectmind.com"
            website = base_url + website_element['href'] if website_element else None
            # 在提取价格信息和网站链接后，继续获取"CONTACT US"内容
            reg_type_element = price_container.find('a', class_='bm-button bm-details-button')
            reg_type = reg_type_element.text.strip() if reg_type_element else None

            # 在提取价格信息和网站链接后，继续获取"FULL - Waitlist Available"内容
            spots_element = price_container.find('span')
            spots = spots_element.text.strip() if spots_element else ""
            print("reg_type",reg_type)
            print("spots",spots)


        event_name = course_event.find("span", {"class": "bm-group-item-name"})
        # print("event name",event_name)
        if event_name:
            info["Event Name"] = event_name.text.strip()
                
        # 定位到指定的div
        target_div = course_event.find('div', class_='bm-group-item-details clearPrerequisite')
                       
        # 找到 target_div 中的所有 div 元素
        div_elements = target_div.find_all('div', class_='bm-group-item-desc')

        # 如果 div_elements 中至少有两个元素
        if len(div_elements) >= 2:
            # 第一个 div 元素是 left
            left = div_elements[0]
                    
            # 第二个 div 元素是 right
            right = div_elements[1]
                
        # 定位到指定的div
        # 找到 left 中的所有 anchor 元素
        anchor_elements = left.find_all('div', class_='anchor') 
                
        # 如果 anchor_elements 中至少有两个元素
        if len(anchor_elements) >= 2:
            # 第一个 anchor 元素是 date
            date = anchor_elements[0]
            # 第三个 anchor 元素是 age
            age = anchor_elements[2]
  
        # 将Beautiful Soup对象转换为字符串
        date_str = str(date)            
        # 例如，提取日期信息
        date_match = re.search(r'aria-label="Event date (.+?)"', date_str)
        if date_match:
            event_date = date_match.group(1)
            # print("Event Date:", event_date)
            if event_date:
                info["Event Date"] = event_date
                
        sessions = course_event.find("span", {"class": "class-sessions-number"})
        if sessions:
            info["Sessions"] = sessions.text.strip()
                
        occurrence_desc = course_event.find("span", {"class": "occurrence"})
        if occurrence_desc:
            info["Occurrence Description"] = occurrence_desc.text.strip()
                    
        age_str=str(age)
        # 例如，提取年龄信息
        age_match = re.search(r'aria-label="Event restrictions (.+?)"', age_str)
        if age_match:
            age_restrictions = age_match.group(1)
            # print("Age Restrictions:", age_restrictions)
            if age_restrictions:
                info["Age Restrictions"] = age_restrictions

        anchor_elements_right = right.find_all('div', class_='anchor') 
        # 如果 anchor_elements 中至少有两个元素
        if len(anchor_elements_right) >= 2:
            # 第一个 anchor 元素是 date
            event_time = anchor_elements_right[0]
            # 第三个 anchor 元素是 age
            event_location = anchor_elements_right[1]
                    
        time_str=str(event_time)
        location_str=str(event_location)
                
        # 提取时间信息
        time_match = re.search(r'aria-label="Event time (.+?)"', time_str)
        if time_match:
            # print("yes, time match")
            event_time = time_match.group(1)
            if event_time:
                info["Event Time"] = event_time

        # 提取位置信息
        location_match = re.search(r'aria-label="Location Name (.+?)"', location_str)
        if location_match:
            # print("yes, location match")
            location_name = location_match.group(1)
            if location_name:
                info["Location"] = location_name                     
        if price:
            info["Price"]=price
        if website:
            info["Website"]=website
        if reg_type:
            info["Reg Type"]=reg_type 
        if spots:
            info["Spots"]=spots
            
        if info is not None:
            data.append(info)
    return data

def find_how_many_course(soup):
    # 定位到包含所有课程信息的 div
    grid_content_div = soup.find('div', class_='bm-grid-content k-grid k-widget')
    # print("grid",grid_content_div)
    if not grid_content_div:
        print("Div with class 'bm-grid-content k-grid k-widget' not found.")
        return []

    # 在 div 中找到所有包含课程信息的 ul 元素
    ul_element = grid_content_div.find('ul', {'data-bind': 'foreach: services'})    
    course_service_elements = ul_element.find_all('course-service', {'params': 'viewModel: $data'})
    len_c=len(course_service_elements)
    return len_c

def set_five_year(driver):
    # 等待 endYear 元素可见
    end_year_element = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "endYear")))
    # 使用 JavaScript 直接设置元素值为 5
    driver.execute_script("arguments[0].value = '5';", end_year_element)

region_code = 'Richmond'
parameters_list=util.get_file_path_dict(region_code)

main_page_licensed_url = parameters_list.get('main_page_licensed_url', None)
paging_interval = parameters_list.get('paging_interval', None)
main_page_loading_time = parameters_list.get('main_page_loading_time', None)
main_page_non_licensed_url = parameters_list.get('main_page_non_licensed_url', None)
times_for_retry = parameters_list.get('times_for_retry', None)

driver = util.get_driver()
url = main_page_licensed_url
# print(url)
driver.get(url)

data = []
link_data = []
time.sleep(5)

def get_Children_data(out_side_position,age_type):
    
    driver = util.get_driver()
    url = main_page_licensed_url
    # print(url)
    driver.get(url)
    
    # 定位到对应的父元素
    # Children = driver.find_element(By.CSS_SELECTOR, f".bm-categorybox:nth-child({out_side_position})")
    # Children = driver.find_element(By.CSS_SELECTOR, ".bm-categorybox:nth-child(3)")
    # 等待元素加载
    wait = WebDriverWait(driver, 20)
    Children = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f".bm-categorybox:nth-child({out_side_position})")))

    # 找到父元素下所有的子元素
    Children_child = Children.find_elements(By.TAG_NAME, "li")



    # 输出子元素数量
    print("Number of child elements:", len(Children_child))

    for i in range (1,len(Children_child)+1):
        
        # print("child",Children_child)

        # 模拟点击第一个链接
        try:
            # driver.get(url)
            driver.find_element(By.CSS_SELECTOR, f".bm-categorybox:nth-child({out_side_position}) li:nth-child({i}) .bm-category-calendar-link:nth-child(1)").click()
            time.sleep(5)
            
            # 获取页面源代码
            html_content_with_dynamic_content = driver.page_source
            # 解析HTML内容
            soup = BeautifulSoup(html_content_with_dynamic_content, 'html.parser')

            wait = WebDriverWait(driver, 10)

            hm_course=find_how_many_course(soup)
            print("hm_coures are :",hm_course)

            for i in range(1, hm_course+1):  # 假设要循环点击前三个 course-service
                # 构造 CSS 选择器
                css_selector = f"course-service:nth-child({i}) .bm-group-expander-text"
                # 点击对应的元素
                driver.find_element(By.CSS_SELECTOR, css_selector).click()
                print("finish clicked:",i)
                time.sleep(3)
                # 获取页面源代码
                html_content_with_dynamic_content = driver.page_source
                # 解析HTML内容
                soup = BeautifulSoup(html_content_with_dynamic_content, 'html.parser')
                get_detail_info(soup,i,data)

            driver.find_element(By.CSS_SELECTOR, ".back-button-label").click()
            time.sleep(8)
            
        except Exception as e:
            print("button cant click")
            continue

    # 关闭浏览器
    driver.close()

    df = pd.DataFrame(data)
    util.save_final_file(df,region_code, file_type = 'list', job_type = age_type)
    util.log_event_list(region_code, 'EV_FINISHED', None, None, None)

    time.sleep(5)




# get_Preschoolers_data()
for out_side_positon in range(2,8):
    if out_side_positon==2:
        age_type="55+yrs"
        # continue
    elif out_side_positon==3:
        age_type="Adults"
    elif out_side_positon==4:
        age_type="Camps"
    elif out_side_positon==5:
        age_type="Children"
    elif out_side_positon==6:
        age_type="Plant Sales"
    elif out_side_positon==7:
        age_type="Preschoolers"
    elif out_side_positon==8:
        age_type="Youth"
    
    get_Children_data(out_side_positon,age_type)
    
