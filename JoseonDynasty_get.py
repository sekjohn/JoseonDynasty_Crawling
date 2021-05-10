from copy import Error
from selenium import webdriver as wd
from selenium import webdriver
import json
from time import sleep
import re
import os
path_ = os.path.dirname(str(os.path.realpath(__file__)))
options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')

driver = wd.Chrome(executable_path=f"{path_}/driver/chromedriver",options=options)

dir_name = "/Joseon_text_list"
url = 'http://sillok.history.go.kr/main/main.do' 

driver.get(url) 
classname = driver.find_element_by_class_name('m_cont_list')
items = classname.find_elements_by_tag_name("li")

#조선 왕 리스트 및 링크 json 만들기
def GetKingList(url):
    if not os.path.exists(path_+dir_name):
        os.makedirs(path_+dir_name)
    driver.get(url) 
    classname = driver.find_element_by_class_name('m_cont_list')
    items = classname.find_elements_by_tag_name("li")
    json_Link = {}
    for i in items:
        json_Link[i.text]=f"{i.find_element_by_tag_name('a').get_attribute('href')}"
    with open(f'{path_}{dir_name}/King_list.json', 'w') as f:
        f.write(json.dumps(json_Link, ensure_ascii=False, indent="\t"))
        f.close()
    return json_Link


#조선 왕 년도 리스트 및 링크 json 만들기
def TheKingHty():
    dict_= {}
    with open(f'{path_}{dir_name}/King_list.json', 'r') as f:
        name_list = json.loads(f.read())
        f.close()  
    for key, value in name_list.items():
        print(key)
        driver.get(url) 
        driver.find_element_by_class_name('m_cont_list')
        driver.execute_script(str(value))

        year_= driver.find_element_by_class_name("tbl_wrap_small")
        items = year_.find_elements_by_tag_name('li')
    

        dict_list =[]
        for i in items:
            B = i.find_element_by_css_selector('a')
            moth = str(B.text)
            filter_ = ['원본 해제 부록 오례 (五禮) 지리지 (地理志) 樂譜']
            
            if not moth in filter_:
                dict_list.append({moth:f"{B.get_attribute('href')}"})
        dict_[str(key)] = dict_list
            
    with open(f'{path_}{dir_name}/King_year_list.json', 'w') as f:
        f.write(json.dumps(dict_, ensure_ascii=False, indent="\t"))
        f.close()

def filter_(text):
    regex = re.compile("[^ㄱ-ㅣ가-힣|.|<|>|,|\"|0-9|\s|\(|\)|]+")

    regex_1  = re.compile(r"\((.*?)\)")
    regex_2  = re.compile(r"(.*?)\)")
    retext = regex.sub(" ",text)
    retext = regex_1.sub("",retext)
    retext = regex_2.sub("",retext)
    space_ = re.compile(",\s")
    retext = space_.sub(",\n",str(retext))
    retext =retext.replace(". ",".\n")
    retext= str(retext).replace("1.","")
    return retext 

#왕 text 파일 크롤링
def m_King_list():
    with open(f'{path_}{dir_name}/King_list.json', 'r') as f:
        name_list1 = json.loads(f.read())
        f.close()  
    
    driver.find_element_by_class_name('m_cont_list')
    for k ,vin in name_list1.items():
        king_name= str(k).replace(" ","").replace("~","")
        if not os.path.exists(path_+f"{dir_name}/{king_name}"):
            os.makedirs(path_+f"{dir_name}/{king_name}")

        with open(f'{path_}{dir_name}/King_year_list.json', 'r') as f:
            name_list = json.loads(f.read())
            f.close() 
        driver.find_element_by_class_name('m_cont_list')
        for key, value in name_list.items():
            driver.execute_script(str(vin))
            if k in key:
                for i in value:
                    
                    moth = i.items()
                    driver.execute_script(str(list(moth)[0][1]))
                    title = driver.find_element_by_xpath("//*[@id='cont_area']/div[1]/div[3]/div/dl/dt")
                    title_1 = driver.find_elements_by_xpath("//*[@id='cont_area']/div[1]/div[3]/div/dl/dd/ul/li")
                    f = open(f'{path_}{dir_name}/{king_name}/{title.text}.txt', 'w')
                    f.write(title.text+"\n")
                    f.write(f"\n")
                    for x in range(len(title_1)+1):
                        try:
                            Link = title_1[x].find_element_by_tag_name('a').get_attribute('href')
                        except:
                            Link = driver.find_element_by_xpath(f"//*[@id='cont_area']/div[1]/div[3]/div/dl/dd/ul/li[{x}]").find_element_by_tag_name('a').get_attribute('href')
                        print("----------------------------------------")
                        print(Link)
                        try:
                            driver.execute_script(str(Link))
                            title_text_name = driver.find_element_by_xpath("//*[@id='cont_area']/div[1]/div[1]/h3")
                            day   = driver.find_element_by_xpath("//*[@id='cont_area']/div[1]/ul[1]/li[6]/a")
                            year = driver.find_elements_by_xpath("//*[@id='cont_area']/div[1]/div[1]/div/span[1]/span/text()")
                            f.write(f"{year.text} - {day.text}\n")
                            f.write(f"<{title_text_name.text}>\n")
                            f.write(f"\n")
                            text_2 = driver.find_element_by_xpath("//*[@id='cont_area']/div[1]/div[3]/div[1]/div/div")
                            text_ = text_2.find_elements_by_tag_name('p')
                            for t in text_:
                                text_ = t
                                re_text= filter_(str(text_.text))
                                print(re_text)
                                f.write(f"{re_text}\n")
                            f.write(f"\n")
                        except:
                            driver.refresh()
                            driver.execute_script(str(Link))
                            title_text_name = driver.find_element_by_xpath("//*[@id='cont_area']/div[1]/div[1]/h3")

                            f.write(f"<{title_text_name.text}>\n")
                            f.write(f"\n")
                            text_2 = driver.find_element_by_xpath("//*[@id='cont_area']/div[1]/div[3]/div[1]/div/div")
                            text_ = text_2.find_elements_by_tag_name('p')
                            for t in text_:
                                text_ = t
                                re_text= filter_(str(text_.text))
                                f.write(f"{re_text}\n")
                            f.write(f"\n")

                        driver.execute_script("window.history.go(-1)")
                    f.close()
                    driver.execute_script("window.history.go(-1)")
            driver.execute_script("window.history.go(-1)")

if __name__ == "__main__":
    try:
        #TheKingHty()
        #TheKingHty()
        m_King_list()
    except Error as e:
        print("Error")
        print(e)
        driver.close() 