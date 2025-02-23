from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import os,time,sys
from seleniumbase import Driver
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd
import xlwings as xw
import traceback
GOOGLE_SCHOLAR_SEARCH_RESULT = https://scholar.google.com/scholar?start={}&q=bio+nanocomposites+for+food+packaging+elsevier&hl=en&as_sdt=0,5&as_ylo=2017&as_yhi=2024/"
import chromedriver_autoinstaller
global_list_index = 181


chromedriver_autoinstaller.install()

for i in range(0,100,10):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options = options)
    driver.delete_all_cookies()

    driver.get(GOOGLE_SCHOLAR_SEARCH_RESULT.format(i))
    time.sleep(8)
    elements_num = driver.find_elements(By.XPATH,"/html/body/div/div[10]/div[2]/div[3]/div[2]/div/div/h3/a")
    print(len(elements_num))
    print(elements_num)
    final_list = []

    for i in range(0,len(elements_num)):
        temp_list = []
        time.sleep(3)



        elements_num[i].click()

        time.sleep(4)
        link = driver.current_url

        # if('pdf' in link):
        #     driver.back()
        
        try:

            research_pub = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='publication-title']/a/span/span"))).text

        except Exception:
            driver.back()
            time.sleep(3)
            continue

        # research_publication = driver.find_element("").text
        
        # research_publication.append(research_pub)

        print(research_pub,"Research Pulication") #Print for debugging
        
        research_tit = driver.find_element(By.XPATH,"//*[@id='screen-reader-main-title']/span").text
        do_i = driver.find_element(By.XPATH,"//*[@id='article-identifier-links']/a[1]/span/span").text

        # research_title.append(research_tit)

        print("Research Title",research_tit)
        time.sleep(2)
        research_dat = ""
        try:

            research_dat = driver.find_element(By.XPATH,"//*[@id='publication']/div[2]/div/a").text

        except Exception:
            try:
                research_dat = driver.find_element(By.XPATH,"/*[@id='publication']/div[2]/div[3]").text

            except Exception:
                print("Research Date Not found")

        # research_date.append(research_dat)

        print("Research Date",research_dat)
        time.sleep(2)

        # doi.append(do_i)

        print("DOI",do_i)
        time.sleep(2)


        try:

            abstr = []
            abs_text = ""
            try:
                

                abstract = driver.find_elements(By.XPATH,"//*[contains(@class,'abstract author')]/div/p")
                print(len(abstract)) 

                for abs in abstract:
                    abstr.append(abs.text)

                abs_text = ''.join(abstr)
                print(abs_text)
            except Exception as err:
                print("Abstract Not found")


            # if(len(abstract>1)):
            #     abs_text = abstract[1].text
            # else:
            #     abs_text = abstract[0].text

            intro_text = ""
            try:
                
                introduction = driver.find_elements(By.XPATH,"//*[contains(@class,'Introduction')]/section/p")

                intro = []
                for intr in introduction:
                    intro.append(intr.text)
                
                intro_text = ''.join(intro)
                print(intro_text)

            except Exception as err:
                print("Sub section Intro")

                try:

                    introduction = driver.find_elements(By.XPATH,"//*[contains(@class,'Body')]/div/section/p")
                    intro = []
                    for intr in introduction:
                        intro.append(intr.text)

                    intro_text = ''.join(intro)
                    print(intro_text)

                except Exception:
                    print("Intro Not found")
            

            temp1 = temp_list.extend([research_pub,research_tit,research_dat,do_i,abs_text,intro_text,link])
            final_list.append(temp1)

            time.sleep(3)
            path = r"C:\Users\Acer\Downloads\Research.xlsx"

            app = xw.App()
            # Connect to )the Excel application
            wb = xw.Book(path)  # Replace 'your_excel_file.xlsx' with your Excel file's name

            # Access the Excel sheet
            sheet = wb.sheets['Sheet1']  # Replace 'Sheet1' with your sheet's name if different

            # Perform the calculation (e.g., sum the values)
            sheet.range(f'B{global_list_index}').value = temp_list
            wb.save(path)
            wb.close()
            app.quit()
        
            driver.back()

            global_list_index+=1
            
        except Exception:
            print(traceback.format_exc())
            time.sleep(3)
            driver.back()
            continue
    driver.quit()
    time.sleep(5)




            
            
