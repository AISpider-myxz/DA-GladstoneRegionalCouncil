import requests
import scrapy
from datetime import datetime
from scrapy.http import Request
from bs4 import BeautifulSoup
from AISpider.items.gladstone_items import GladstoneItem
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month_
from common.set_date import get_this_month

# 三个选项
# 都是一次出全部结果
# 如果需要按时间找需要再搜索列表结果页传时间参数

class GladstoneSpiderSpider(scrapy.Spider):
    name = "gladstone"
    allowed_domains = ["online.gladstone.qld.gov.au"]
    start_urls = ["https://online.gladstone.qld.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx?ModuleCode=LAP"]

    custom_settings = {
            'DOWNLOAD_DELAY': 3,
            'LOG_STDOUT': True,
            #'LOG_FILE': 'scrapy_gladstone.log',
            'DOWNLOAD_TIMEOUT': 1200
        }

    def __init__(self, run_type='all',category=None,days=None ):
        """
        runtype: 指定爬虫的运行方式 all爬取一直以来所有数据， part指定date_runge爬取部分数据
        date_range:爬取数据的时间范围
        """
        self.run_type = run_type
        self.category = category
        if days == None:
        # 如果没有传days默认为这个月的数据
            self.days = get_this_month()
        else:
            now = datetime.now()
            days = int(days)
            date_from = (now - timedelta(days)).date().strftime('%d/%m/%Y')
            # 这里计算出开始时间 设置到self.days
            self.days = date_from
        self.cookies = {}

    def judge_list_nums(self,resp):
        # 返回列表数和页数
        soup = BeautifulSoup(resp, 'html.parser')
        temp_list = []
        try:
            page_num = soup.select_one('#ctl00_MainBodyContent_mPagingControl_pageNumberLabel').get_text().split(' ')[-1]
            page_num = int(page_num)
        except:
            page_num = 1
        try:
            list_nums = len(soup.select('tbody tbody .ContentPanel'))+len(soup.select('tbody tbody .AlternateContentPanel'))
        except:
            list_nums = 0
        app_ids =[]
        if list_nums != 0:
            temp_ids = soup.select('#ctl00_MainBodyContent_GeneralEnquiryDynamicColumnDiv td a')
            for i in temp_ids:
                app_ids.append(i.get_text())
        temp_list.append(page_num)
        temp_list.append(list_nums)
        temp_list.append(app_ids)
        return(temp_list)

    def parse(self, response):
        if self.run_type == 'all':
            for item in self.get_first():
                yield item
            for item in self.get_second():
                yield item
            for item in self.get_third():
                yield item
        elif self.run_type == 'first':
            for item in self.get_first(days=self.days):
                yield item
        elif self.run_type == 'second':
            for item in self.get_second(days=self.days):
                yield item
        elif self.run_type == 'third':
            for item in self.get_third(days=self.days):
                yield item
        
    def get_first(self,days=None):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get("https://online.gladstone.qld.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx?ModuleCode=LAP")
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl02_ctl00"]'))).click()
        #WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl03_ctl00"]'))).click()
        #WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl04_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mContinueButton"]'))).click()
        if days != None:
            start_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl04_mFromDatePicker_dateTextBox"]')
            end_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl04_mToDatePicker_dateTextBox"]')
            start_time.clear()
            end_time.clear()
            start_time.send_keys(self.days)
            end_time.send_keys(datetime.now().date().strftime('%d/%m/%Y'))
            search = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]').click()

        temp_list = self.judge_list_nums(resp=browser.page_source)
        page_nums = temp_list[0]
        for i in range(page_nums):
            for item in self.click_detail1(temp_list=temp_list,browser=browser):
                yield item
            try:
                WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mPagingControl_nextPageHyperLink"]'))).click()
                temp_list = self.judge_list_nums(resp=browser.page_source)
            except:
                print('end')
    def get_second(self,days=None):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get("https://online.gladstone.qld.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx?ModuleCode=LAP")
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend'))).click()
        #WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl02_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl03_ctl00"]'))).click()
        #WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl04_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mContinueButton"]'))).click()
        
        if days != None:
            start_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl04_mFromDatePicker_dateTextBox"]')
            end_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl04_mToDatePicker_dateTextBox"]')
            start_time.clear()
            end_time.clear()
            start_time.send_keys(self.days)
            end_time.send_keys(datetime.now().date().strftime('%d/%m/%Y'))
            search = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]').click()

        temp_list = self.judge_list_nums(resp=browser.page_source)
        page_nums = temp_list[0]
        for i in range(page_nums):
            for item in self.click_detail2(temp_list=temp_list,browser=browser):
                yield item
            try:
                WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mPagingControl_nextPageHyperLink"]'))).click()
                temp_list = self.judge_list_nums(resp=browser.page_source)
            except:
                print('end')

    def get_third(self,days=None):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get("https://online.gladstone.qld.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx?ModuleCode=LAP")
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend'))).click()
        #WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl02_ctl00"]'))).click()
        #WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl03_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl04_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mContinueButton"]'))).click()
        
        if days != None:
            start_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl04_mFromDatePicker_dateTextBox"]')
            end_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl04_mToDatePicker_dateTextBox"]')
            start_time.clear()
            end_time.clear()
            start_time.send_keys(self.days)
            end_time.send_keys(datetime.now().date().strftime('%d/%m/%Y'))
            search = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]').click()

        temp_list = self.judge_list_nums(resp=browser.page_source)
        page_nums = temp_list[0]
        for i in range(page_nums):
            for item in self.click_detail3(temp_list=temp_list,browser=browser):
                yield item
            try:
                WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mPagingControl_nextPageHyperLink"]'))).click()
                temp_list = self.judge_list_nums(resp=browser.page_source)
            except:
                print('end')
    def click_detail1(self,temp_list,browser):
        page_num = temp_list[0]
        list_nums = temp_list[1]
        app_ids = temp_list[2]
        for i in range(list_nums):
            nums = i+2
            # 点击进入详情页
            WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,f'//*[@id="gridResults"]/tbody/tr[{nums}]/td[1]/div/a'))).click()
            for item in self.parse1(resp=browser.page_source,app_id=app_ids[nums+1],):
                yield item
            # 点击返回列表页                                                            
            WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mBackButton"]'))).click()
    
    def click_detail2(self,temp_list,browser):
        page_num = temp_list[0]
        list_nums = temp_list[1]
        app_ids = temp_list[2]
        for i in range(list_nums):
            nums = i+2
            # 点击进入详情页
            WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,f'//*[@id="gridResults"]/tbody/tr[{nums}]/td[1]/div/a'))).click()
            for item in self.parse2(resp=browser.page_source,app_id=app_ids[nums+1],):
                yield item
            # 点击返回列表页                                                            
            WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mBackButton"]'))).click()
    
    def click_detail3(self,temp_list,browser):
        page_num = temp_list[0]
        list_nums = temp_list[1]
        app_ids = temp_list[2]
        for i in range(list_nums):
            nums = i+2
            # 点击进入详情页
            WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,f'//*[@id="gridResults"]/tbody/tr[{nums}]/td[1]/div/a'))).click()
            for item in self.parse3(resp=browser.page_source,app_id=app_ids[nums+1],):
                yield item
            # 点击返回列表页                                                            
            WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mBackButton"]'))).click()
    
    def parse1(self, resp,app_id,):
        """
        访问详情页， 获取所有信息
        """
        item = GladstoneItem()
        item['application_id'] = app_id
        soup = BeautifulSoup(resp, 'html.parser')
        # details
        item['description'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Application_Description_1206 .AlternateContentText').get_text()
        #item['submit'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Lodgement_Date_1207 .AlternateContentText').get_text()
        try:
            lodged_date = soup.select_one('#ctl00_MainBodyContent_DynamicField_Lodgement_Date_1207 .AlternateContentText').get_text()
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['submit'] = temp_data if lodged_date else 0  
        except:
            item['submit'] = 0
        
        item['status'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Status_1208 .AlternateContentText').get_text()
        item['address'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Formatted_Application_Location_1209 .AlternateContentText').get_text()
        item['site_address'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Overriding_Site_Address_2307 .AlternateContentText').get_text()
      
        # decision
        decision = soup.select('#ctl00_MainBodyContent_group_1496 .ContentPanel .ContentPanel td')
        temp_str = ''
        for i in decision:
            temp_str += i.get_text()+','
        item['decision'] = temp_str.strip('\n')

        # Applicant
        try:
            applicant = soup.select_one('#ctl00_MainBodyContent_group_1497 .ContentPanel .ContentPanel .ContentText').get_text()
            item['names'] = applicant
        except:
            item['names'] = ''
        #print(item)
        yield item
    def parse2(self, resp,app_id,):
        """
        访问2详情页， 获取所有信息
        """
        item = GladstoneItem()
        item['application_id'] = app_id
        soup = BeautifulSoup(resp, 'html.parser')
        # details
        item['description'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Application_Description_1126 .AlternateContentText').get_text()
        #item['submit'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Lodgement_Date_1207 .AlternateContentText').get_text()
        try:
            lodged_date = soup.select_one('#ctl00_MainBodyContent_DynamicField_Lodgement_Date_1127 .AlternateContentText').get_text()
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['submit'] = temp_data if lodged_date else 0  
        except:
            item['submit'] = 0
        
        item['status'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Status_1128 .AlternateContentText').get_text()
        item['address'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Formatted_Application_Location_1129 .AlternateContentText').get_text()
        item['site_address'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Overriding_Site_Address_2308 .AlternateContentText').get_text()
      
        # decision
        decision = soup.select('#ctl00_MainBodyContent_group_1490 .ContentPanel .ContentPanel td')
        temp_str = ''
        for i in decision:
            temp_str += i.get_text()+','
        item['decision'] = temp_str.strip('\n')

        # Applicant
        try:
            applicant = soup.select_one('#ctl00_MainBodyContent_group_1491 .ContentPanel .ContentPanel .ContentText').get_text()
            item['names'] = applicant
        except:
            item['names'] = ''

        '''这里的代码有用，可以取到documents的链接，但是链接不是一个固定的pdf的链接，是一个固定的链接需要传参数才能请求到pdf'''
        # judge_document = soup.select_one('#ctl00_MainBodyContent_mHyperLinkAttachments')
        # if judge_document:
        #     # documents
        #     WebDriverWait(browser,5,0.5).until(EC.element_to_be_clickable((By.ID,'ctl00_MainBodyContent_mHyperLinkAttachments'))).click()
        #     soup = BeautifulSoup(browser.page_source, 'html.parser')
        #     temp_documents = soup.select('.AlternateContentPanel tbody tr a')
        #     documents = ''
        #     for d in temp_documents:
        #         documents += d.get('href')+';'
        #     item['documents'] = documents
        #     WebDriverWait(browser,5,0.5).until(EC.element_to_be_clickable((By.ID,'#ctl00_MainBodyContent_mBackButton'))).click()

        #print(item)
        
        yield item
    def parse3(self, resp,app_id,):
        """
        访问3详情页， 获取所有信息
        """
        item = GladstoneItem()
        item['application_id'] = app_id
        soup = BeautifulSoup(resp, 'html.parser')
        # details
        item['description'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Application_Description_2316 .AlternateContentText').get_text()
        #item['submit'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Lodgement_Date_1207 .AlternateContentText').get_text()
        try:
            lodged_date = soup.select_one('#ctl00_MainBodyContent_DynamicField_Lodgement_Date_2318 .AlternateContentText').get_text()
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['submit'] = temp_data if lodged_date else 0  
        except:
            item['submit'] = 0
        
        item['status'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Status_2319 .AlternateContentText').get_text()
        item['address'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Formatted_Application_Location_2317 .AlternateContentText').get_text()
        item['site_address'] = soup.select_one('#ctl00_MainBodyContent_DynamicField_Overriding_Site_Address_2320 .AlternateContentText').get_text()
      
        # decision
        decision = soup.select('#ctl00_MainBodyContent_group_2522 .ContentPanel .ContentPanel td')
        temp_str = ''
        for i in decision:
            temp_str += i.get_text()+','
        item['decision'] = temp_str.strip('\n')

        # Applicant
        try:
            applicant = soup.select_one('#ctl00_MainBodyContent_group_2523 .ContentPanel .ContentPanel .ContentText').get_text()
            item['names'] = applicant
        except:
            item['names'] = ''

        '''这里的代码有用，可以取到documents的链接，但是链接不是一个固定的pdf的链接，是一个固定的链接需要传参数才能请求到pdf'''
        # judge_document = soup.select_one('#ctl00_MainBodyContent_mHyperLinkAttachments')
        # if judge_document:
        #     # documents
        #     WebDriverWait(browser,5,0.5).until(EC.element_to_be_clickable((By.ID,'ctl00_MainBodyContent_mHyperLinkAttachments'))).click()
        #     soup = BeautifulSoup(browser.page_source, 'html.parser')
        #     temp_documents = soup.select('.AlternateContentPanel tbody tr a')
        #     documents = ''
        #     for d in temp_documents:
        #         documents += d.get('href')+';'
        #     item['documents'] = documents
        #     WebDriverWait(browser,5,0.5).until(EC.element_to_be_clickable((By.ID,'#ctl00_MainBodyContent_mBackButton'))).click()

        #print(item)
        del item['metadata']
        yield item
