import logging
import socket
import datetime
import os
import argparse

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# from sqlalchemy import create_engine

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Description of your script.')
    parser.add_argument('--cfg'         , type=str, default=None, help='Path to the configuration file.')
    parser.add_argument('--start_index' , type=int, default=0, help='Start index for data retrieval.')
    parser.add_argument('--end_index'   , type=int, help='End index for data retrieval.')
    parser.add_argument('--db'   , type=str, help='Input the database name')
    parser.add_argument('--excel_name'   , type=str, help='Input the excel path')
    parser.add_argument('--date'   , type=str, help='Enter the date in format YYYY/MM/DD to get the correct file.')
    # parser.add_argument('--license', action='store_true', help='Use licensed URL')
    # parser.add_argument('--non_license', dest='license', action='store_false', help='Use non-licensed URL')
    return parser.parse_args()


def read_control_config(file_path, parameters,prefix):
    """
    Reads an Excel file containing settings, extracts specific parameters
    based on the provided list of parameter names, and returns them as a list.

    Parameters:
    - file_path (str): Path to the Excel file.
    - parameters (list): List of parameter names to extract.

    Returns:
    - list: Extracted parameters if a matching row is found, otherwise returns None.
    """
    # Read the Excel file
    settings_df = pd.read_excel(file_path)

    # Find the row where PREFIX is 'CA-ON'
    prefix_row = settings_df[settings_df['PREFIX'] == prefix]

    # Check if any matching row is found
    if not prefix_row.empty:
        # Extract the required parameters
        extracted_parameters = [prefix_row[param].values[0] for param in parameters]

        # Return the parameters as a list
        return extracted_parameters
    else:
        # If no matching row is found, return None
        return None
    


########################################################################################
# Init ChromeDriver, return a driver, you should call driver.quit() 
########################################################################################
# If uising VISACOMPUTER3: 
# Read the chrome dirver path specificly
# Downloading chromedriver and corresponding chrome from:
# https://googlechromelabs.github.io/chrome-for-testing/
# chrome_path = 'C:/Users/VISACPDCOMPUTER3/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe'

def get_driver():
    # chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    chromedriver_path = None
    if chromedriver_path is not None:
        print(f'Chromedriver path found in environment variables: {chromedriver_path}')
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service)
    else:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        
        # Check if in test env
        # If in, add 2 chrome options
        mode = os.environ.get('PROL_RUN_MODE')
        if mode is not None:
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        
    return driver

########################################################################################
# Setting the program Log 
########################################################################################
def initialize_logging(region_code, file_type, job_type = None):
    if not job_type:
        job_type = "contractor"
    
    log_file=f'{job_type}_{file_type}_{region_code}.log'
    logging.basicConfig(filename=log_file, level=logging.INFO, format='- %(message)s')

def log_event(prefix, event_type, config_file_path, start_index, urls, total_num_exceptions, current_index, exception, is_umbrella):
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    current_time = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')

    if event_type == 'EV_STARTED':
        summary = log_event_init(config_file_path, start_index, urls)
    elif event_type == 'EV_FINISHED':
        summary = log_event_finish(total_num_exceptions, urls, start_index)
    elif event_type == 'EV_EXCEPTION':
        summary = log_event_exception(urls[current_index], exception)
    elif event_type == 'EV_ABORTED':
        summary = 'Task aborted due to some reason'
    elif event_type == 'EV_RUNNING':
        summary = log_event_running(current_index, urls, is_umbrella)
    else:
        logging.warning(f"Unknown event type: {event_type}")

    log_message = f"{current_time} - {host_name}/{host_ip}/{prefix}/CONTRACTOR/{event_type}/ - {summary}"
    logging.info(log_message)

def log_event_init(config_file_path, start_index, urls):
    config_info = f"configuration reading from {config_file_path}"
    total_records = len(urls) - start_index
    estimated_time_minutes = total_records * 0.1
    log_text = f"\n{config_info}, \nnumber of total records: {total_records}, \nestimated time: {estimated_time_minutes} mins "
    return log_text

def log_event_running(current_index, urls, is_umbrella):
    if is_umbrella:
        log_text = f"\nThis company: {urls[current_index]} is an umbrella company, being skipped"
    else:
        curr_info = f"current working on {current_index+1}"
        total_records = len(urls)
        progress_info = f"{current_index+1}/{total_records}"
        log_text = f"\n{curr_info}, \ncurrent progress: {progress_info}, \nestimated time: 10 secs."
    return log_text

def log_event_exception(url, exception):
    log_text = f"\nError processing URL {url}: {exception}"
    return log_text

def log_event_finish(total_num_exceptions, urls, start_index):
    total_records = len(urls) - start_index
    log_text = f"\ntotal number of exceptions/total records: {total_num_exceptions}/{total_records}\n\n"
    return log_text

########################################################################################
########################################################################################
def log_event_list(prefix, event_type, num_of_county, current_county, exception,page_num =None):
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    current_time = datetime.now().strftime('%Y%m%d %H:%M:%S')

    if event_type == 'EV_STARTED':
        log_text = f"\nThere are {num_of_county} parts in total"
        summary = log_text
    elif event_type == 'EV_FINISHED':
        summary = f"\nFinish all url list excracting for {prefix}"
    elif event_type == 'EV_EXCEPTION':
        summary = f"\nAn error occurred in this part:{current_county}, exception is: {str(exception)}"
    elif event_type == 'EV_ABORTED':
        summary = 'Task aborted due to some reason'
    elif event_type == 'EV_RUNNING':
        summary = f"\nCurrently working on {current_county}, page number: {page_num}"
    else:
        logging.warning(f"Unknown event type: {event_type}")
        
    log_message = f"{current_time} - {host_name}/{host_ip}/{prefix}/CONTRACTOR/{event_type}/ - {summary}"
    logging.info(log_message)


def save_excel(df,final_file_path):
    df.to_excel(final_file_path, index=False)
    
def save_sql(df, table_name, engine):
    """
    将 DataFrame 中的数据保存到 MySQL 数据库
    :param df: DataFrame，要保存的数据
    :param table_name: str，要保存到的数据库表名
    :param engine: SQLAlchemy Engine 对象，数据库连接
    """
    try:
        # 将 DataFrame 中的数据保存到 MySQL 数据库
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print("数据成功保存到 MySQL 数据库中！")
    except Exception as e:
        print("保存数据到 MySQL 数据库时出错：", e)
        
# def parse_command_line_args():
#     parser = argparse.ArgumentParser(description='Description of your script.')
#     parser.add_argument('--cfg', type=str, default=r'./CFG-Parameters.xlsx', help='Path to the configuration file.')
#     args = parser.parse_args()
#     return args

def get_file_path_dict(region_code):
    config_file_path = r'./BaseUrl.xlsx'
    if __name__ == "__main__":
        # 解析命令行参数
        args = parse_command_line_args()
        # 根据用户输入更新默认路径
        config_file_path = args.cfg if args.cfg else r'./BaseUrl.xlsx'   
         
    excel_file_path = config_file_path
    parameters = ['Paging Interval', 'Main Page Loading Time', 'Main Page URL','Main Page Non Licensed URL','Times for Retry','Detail Click Interval',
              'Times for Retry',
              'Buffer of Flush',
              'Starting time for Detail Loading',
              'Starting time for Detail Retry',
              'Retry Interval']
    parameters_list = read_control_config(excel_file_path, parameters, region_code)

    parameters_dict = {}  # 创建空字典用于存储参数

    if parameters_list:
        # 将参数列表转换为字典
        parameters_dict = {
            'paging_interval': parameters_list[0],
            'main_page_loading_time': parameters_list[1],
            'main_page_licensed_url': parameters_list[2],
            'main_page_non_licensed_url': parameters_list[3],
            'times_for_retry': parameters_list[4],
            'detail_click_interval':parameters_list[5],
            'times:_for_retry':parameters_list[6],
            'buffer_of_flush':parameters_list[7],
            'starting_time_for_detail_loading':parameters_list[8],
            'starting_time_for_detail_retry':parameters_list[9],
            'retry_interval':parameters_list[10]
        }
        
        print(parameters_dict)
        # 根据需要添加其他参数
    else:
        print(f"No matching row found for PREFIX = {region_code}.")

    return parameters_dict


def get_file_path_detail_partial(region_code):
    current_datetime = datetime.now().strftime("%Y%m%d")
    partial_save_path = f'./data/contractor_detail_{region_code}_partial-{current_datetime}'
    return partial_save_path

def save_partial(df,save_counter, region_code):
    current_datetime = datetime.now().strftime("%Y%m%d")
    # output_file_path = rf"./data/{region_code}-{job_type}-{file_type}-{current_datetime}.xlsx"
    save_path = rf'./data/{region_code}-partial_data{save_counter}-{current_datetime}.xlsx'
    df.to_excel(save_path, index = False)
    print(f"Data has been saved to {save_path}")
    
from datetime import datetime

def save_final_file(df, region_code, file_type, job_type=None):
    if not job_type or job_type == "contractor" :
        job_type = "contractor"
    
    job_type = job_type.upper()   
    file_type = file_type.upper()
 
    try:
        # Specify the output file path
        current_datetime = datetime.now().strftime("%Y%m%d")
        output_file_path = rf"./data/{region_code}-{job_type}-{file_type}-{current_datetime}.xlsx"
        # output_file_path = rf"./data/{region_code}-{job_type}-{file_type}.xlsx"
        df.to_excel(output_file_path, index=False)
        print(f"Excel file saved to: {output_file_path}")

    except Exception as e:
        current_datetime = datetime.now().strftime("%Y%m%d-%H%M")
        output_file_path = rf"./data/{region_code}-{job_type}-{file_type}-{current_datetime}.xlsx"
        # Save the data
        df.to_excel(output_file_path, index=False)
        print(f"Excel file saved to: {output_file_path}")
  

def get_country_states(country):
    if country == "CA":
        ca_states = [
            "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
            "Northwest Territories", "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island",
            "Quebec", "Saskatchewan", "Yukon"
        ]
        final_states = ca_states
    else:
        us_states = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
            "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
            "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
            "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
            "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
            "American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico", "United States Minor Outlying Islands",
            "Virgin Islands, U.S.", "District of Columbia"
        ]
        final_states = us_states
    return final_states

# def read_list_file_path(region_code, file_type, job_type=None, file_date=None):
#     if not job_type or job_type == "contractor":
#         job_type = "contractor"
    
#     job_type = job_type.upper()   
#     file_type = file_type.upper()
    
#     if not file_date:
#         list_file_path = rf"./data/{region_code}-{job_type}-{file_type}.xlsx"
#     else:
#         list_file_path = rf"./data/{region_code}-{job_type}-{file_type}-{file_date}.xlsx"
    
#     return list_file_path

def read_list_file_path(region_code, file_type, job_type=None, file_date=None):
    if not job_type or job_type == "contractor":
        job_type = "contractor"
    
    job_type = job_type.upper()   
    file_type = file_type.upper()
    
    if not file_date:
        list_file_path = rf"./data/{region_code}-{job_type}-{file_type}.xlsx"
    else:
        list_file_path = rf"./data/{region_code}-{job_type}-{file_type}-{file_date}.xlsx"
    
    return list_file_path



def get_cities_CA():
    canadian_cities = [
        'Dryden', 'South Bruce Peninsula', 'Vegreville', 'Terrebonne', 'Lachute', 'Minto', 'Digby', 'Sainte-Marie', 
        'Holland', 'Plum Coulee', 'Smithers', 'Halifax', 'Belmont', 'Sudbury', 'Pont-Rouge', 'Kenton', 'Pilot Mound', 
        'Morris', 'Rimbey', 'Holmfield', 'Binscarth', 'Prince Albert', "St. John's", 'Blackfalds', 'Kamsack', 
        'Campbell River', 'Island Lake', 'Duncan', 'Winkler', 'Victoriaville', 'Vancouver', 'Sackville', 'Baie-Comeau', 
        'Labrador City', 'Stanley', 'Pikwitonei', 'Leduc', 'Courtenay', 'Prince George', 'Milton', 'Nanaimo', 'Trail', 
        'Inuvik', 'Baldur', 'Austin', 'Pembroke', 'Williams Lake', 'Antigonish', 'Selkirk', 'High River', 
        'Salaberry-de-Valleyfield', 'Thunder Bay', 'Roblin', 'Lethbridge', 'Saint-Lin-Laurentides', "L'Assomption", 
        'Ste. Anne', 'Somerset', 'London', 'Moncton', 'Welland', 'Happy Valley-Goose Bay', 'Castlegar', 'Timmins', 
        'Gods Lake Narrows', 'Ethelbert', 'Shilo', 'North Vancouver', 'Bathurst', 'Kentville', 'Matagami', 
        'Chestermere', 'St. Albert', 'Ochre River', 'Matane', 'Cranbrook', 'Belleville', 'Elmira', 'Bromont', 
        'Coaldale', 'Windsor', 'Blainville', 'Hanover', 'Reston', 'Dieppe', 'Pitt Meadows', 'Port Hawkesbury', 
        'Medicine Hat', 'Rosetown', 'Snowflake', 'Sainte-Agathe-des-Monts', 'Stonewall', 'Winnipeg', 'Grandview', 
        'Hawkesbury', 'Oak Point', 'Rivière-du-Loup', 'La Broquerie', 'Sylvan Lake', 'Grand Rapids', 'Warman', 
        'Petawawa', 'Souris', 'Waterloo', 'Thompson', 'Fort Frances', 'Fredericton', 'Boissevain', 'Richmond', 
        'Gander', 'Leamington', 'Surrey', 'Notre-Dame-de-Lourdes', 'Revelstoke', 'Alma', 'Pierson', 'Salmon Arm', 
        'Raymond', 'Strathclair', 'Birtle', 'Amherstburg', 'Mascouche', 'Cobourg', 'Parry Sound', 'Langley', 
        'White Rock', 'Port Coquitlam', 'Carberry', 'Calgary', 'Armstrong', 'Delta', 'Gravenhurst', 'Hudson', 
        'Treherne', 'Carman', 'La Tuque', 'Montreal', 'Quesnel', 'Langford', 'Aurora', 'Sept-Îles', 'Boisbriand', 
        'Victoria Beach', 'New Glasgow', 'Carmen', 'Prince Rupert', 'Lively', 'Mirabel', 'Penticton', 'Port Colborne', 
        'Nelson', 'Woodstock', 'Edmonton', 'Saguenay', 'Stratford', 'Amos', 'Thetford Mines', 'Moose Jaw', 
        'Ste. Rose du Lac', 'Winnipeg Beach', 'Kincardine', 'Hamiota', 'Hamilton', 'Beausejour', 'Coulter', 'Elgin', 
        'Whitehorse', 'Kelowna', 'Parksville', 'Red Deer', 'Campbellton', 'Stettler', 'Joliette', 'Chetwynd', 
        'Split Lake', 'The Pas', 'Princeville', 'Dartmouth', 'Elk Point', 'Maple Ridge', 'Manitou', 'Coquitlam', 
        'Norfolk County', 'Grand Forks', 'Fort Erie', 'Brandon', 'Merritt', 'Chilliwack', 'Victoria', 'Pipestone', 
        'Rorketon', 'Saint-Hyacinthe', 'Aylmer', 'Lac du Bonnet', 'Shamattawa', 'Guelph', "Val-d'Or", 'Wabowden', 
        'Kindersley', 'Minitonas', 'Kamloops', 'Waskada', 'Baie-Saint-Paul', 'Saskatoon', 'Peterborough', 'Dauphin', 
        'Spruce Grove', 'New Westminster', 'Alexander', 'Powerview-Pine Falls', 'West Kelowna', 'Greenwood', 'Huntsville', 
        'Sainte Rose du Lac', 'Sherbrooke', 'Snow Lake', 'Colwood', 'Morden', 'Valleyview', 'Norway House', 'Cold Lake', 
        'Powell River', 'Fort Saskatchewan', 'Creighton', 'Gretna', 'Stephenville', 'Ottawa', 'Magog', 'Kitchener', 
        'La Sarre', 'Wetaskiwin', 'Melita', "L'Île-Perrot", 'Nesbitt', 'Kimberley', 'Sprague', 'Saint John', 'Rossland', 
        'Lynn Lake', 'Port Alberni', 'Fernie', 'Pine River', 'Trois-Rivières', 'Stony Plain', 'Orillia', 'Rimouski', 
        'Sandy Bay', 'Mont-Laurier', 'Leaf Rapids', 'Wasaga Beach', 'Airdrie', 'Abbotsford', 'Sainte-Thérèse', 'Lac-Mégantic', 
        'St. Claude', 'Wawanesa', 'Fort St. John', 'Niverville', 'Nelson House', 'Cochrane', 'Clarenville', 'North Bay', 
        'Russell', 'Cormorant', 'Sperling', 'Lacombe', 'St. Andrews', 'Fort McMurray', 'La Prairie', 'New Richmond', 
        'Bissett', 'Whitemouth', 'Clarence-Rockland', 'South Huron', 'Sault Ste. Marie', 'Cartwright', 'Enderby', 
        'Gimli', 'Riverview', 'Gilbert Plains', 'Dawson Creek', 'Grimsby', 'Cross Lake', 'Cypress River', 'Churchill', 
        'Teulon', 'Miramichi', 'Sainte-Julie', 'Caledon', 'York Landing', 'Portage la Prairie', 'Vernon', 'Glenboro', 
        'Port Moody', 'Rapid City', 'Kirkland Lake', 'Owen Sound', 'Slave Lake', 'Brooks', 'Elora', 'Lloydminster', 
        'Lorraine', 'Black Diamond', 'Lyleton', 'Edson', 'Gillam', 'Mafeking', 'Terrace', 'Shoal Lake', 'MacGregor', 
        'Chicoutimi', 'Ponoka', 'Deloraine', 'Midland', 'Swan River', 'Camrose', 'Brantford', 'Burnaby', 'Minnedosa', 
        'Collingwood', 'Quebec%20City', 'Killarney', 'Iqaluit', 'Kapuskasing', 'Carleton Place', 'Barrie', 'Lauder', 
        'St. Catharines', 'Regina', 'Toronto', 'Steinbach', 'Odanah', 'Hearst', 'Emerson', 'Hartney', 'Saint-Lazare', 
        'Yellowknife', 'Rivers', 'Flin Flon', 'Gods River', 'Grande Prairie', 'Altona', 'Cape Breton', 'Kingston', 
        'Edmundston', 'Virden', 'McCreary', 'Wood Buffalo', 'Essex', 'Rossburn', 'Creston', 'Neepawa', 'Nipawin', 
        'Smiths Falls'
    ]
    return canadian_cities

def initialize_dict():
    info = {
            'URL': '',
            'Name': '',
            'Email': '',
            'Tags': '',
            'BusinessName': '',
            'TradeName(DBA)': '',
            'LicenseType': '',
            'LicenseNumber': '',
            'LicenseState': '',
            'Effective Date': '',
            'Expiration Date': '',
            'Phone': '',
            'CellPhone': '',
            'Members': '',
            'Fax': '',
            'Address': '',
            'Website': ''
        }
    return info
