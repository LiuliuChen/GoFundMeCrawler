import logging
import time
import requests
import utils
import datetime
from data.constant import cafile
import re
import json
import socket
from requests.adapters import HTTPAdapter

"""Extract information from individual campaign page"""

class IndividualPageInfoExtractor(object):
    def __init__(self, url):
        try:
            self.url = url
            soup = utils.get_fresh_soup(url)
            self.soup = soup
            script = soup.find_all('script', limit=2)[1].get_text()
            self.script_data = json.loads(re.findall(r'window\.initialState = ({.*?});', script)[0])
            default_url = url.replace('https://www.gofundme.com/f/', '')
            if '?' in default_url:
                default_url = default_url.split('?')[0]
            self.default_url = default_url
            self.comment_counts = 0

        except Exception as e:
            logging.exception(e)

    def getCollectedDate(self):
        today = datetime.date.today()
        formatted_today = today.strftime('%Y-%m-%d')
        return formatted_today

    def getCreatedDate(self):
        try:
            created_date = self.script_data['feed']['campaign']['created_at']
            return created_date
        except Exception as e:
            logging.exception(e)

    def getCampaignName(self):
        try:
            campaign_name = self.soup.find('h1', class_="a-campaign-title")
            return campaign_name.get_text(strip=True)
        except Exception as e:
            logging.exception(e)

    def getLocation(self):
        try:
            location = self.script_data['feed']['campaign']['location']
            return location
        except Exception as e:
            logging.exception(e)

    def getFundraisingTeam(self):
        try:
            whole_team = []
            team = self.script_data['feed']['team_members']
            for i in team:
                member ={'name': i['first_name']+' '+i['last_name'], 'role': i['role'], 'locale': i['locale']}
                whole_team.append(member)
            # organization = []  # would have more than one organization
            # organization_info = self.soup.find('div', class_="m-campaign-members-main-organizer")
            # organization = organization_info.find('div', class_='m-person-info-name').get_text(strip=True)
            return whole_team
        except Exception as e:
            logging.exception(e)

    def getBeneficiary(self):
        try:
            beneficiary_info = self.soup.find('div', class_="m-campaign-members-main-beneficiary")
            if beneficiary_info:
                if beneficiary_info.find('span'): # organization
                    beneficiary = beneficiary_info.span.get_text()
                else:
                    beneficiary = beneficiary_info.find('div', class_='m-person-info-name').get_text(strip=True)
                return beneficiary
            else:
                return None
        except Exception as e:
            logging.exception(e)

    def getDescription(self):
        try:
            description = self.soup.find('div', class_="o-campaign-description").get_text('\n', strip=True)
            description = description.replace('Read more', '') # delete the read more icon
            return description
        except Exception as e:
            logging.exception(e)


    def getUpdate(self):
        try:
            update_info = {}
            update_div = self.soup.find('div', class_='p-campaign-updates')
            pattern = re.compile(r'\d+')
            update_num = pattern.findall(update_div.find('h2').get_text())[0]
            update_info['number'] = int(update_num)

            # find when the updates were made
            content = update_div.find('header', class_='m-update-info').find_all('span')
            update_info['time'] = utils.time_formatter(content[0].get_text(strip=True))

            if int(update_num) == 1:
                pass
            else:
                pass

        except Exception as e:
            logging.exception(e)


    def getDonationInfo(self):
        try:
            # store donation info
            donation_info = {"raised_money": '', "goal": ''}
            progress = self.soup.find('h2', class_='m-progress-meter-heading').get_text(strip=True).replace(',', '')
            # print('string"', progress)
            pattern = re.compile(r'\d+')
            progress = pattern.findall(progress)
            donation_info['raised_money'], donation_info['goal'] = progress[0], progress[1]
            # not working
            # progress = self.soup.find('div', class_='o-campaign-sidebar-wrapper').contents[1].find_all('li')
            # donation_info["donors"] = progress[0].find('span').get_text(strip=True)
            # donation_info["shares"] = progress[1].find('span', class_='text-stat-value').get_text(strip=True)
            # donation_info["followers"] = progress[2].find('span', class_='text-stat-value').get_text(strip=True)

            return donation_info

        except Exception as e:
            logging.exception(e)

    def getComment(self):
        try:
            comments = self.soup.find('div', class_='p-campaign-comments').find('h2').get_text(strip=True)
            pattern = re.compile(r'\d+')   # find the integer
            comments_num = pattern.findall(comments)[0]
            return comments_num
        except Exception as e:
            logging.exception(e)


    def getDonationList(self):
        try:
            socket.setdefaulttimeout(3)  # timeout 3
            see_all = self.soup.find('div', class_='show-for-large')
            see_all_link = 'https://www.gofundme.com'+see_all.find('a').get('href')
            new_page = utils.get_fresh_soup(see_all_link)
            script_text = new_page.find_all('script')[1].get_text()
            data = json.loads(re.findall(r'window\.initialState = ({.*?});', script_text)[0])
            donation_list = data['feed']['donations'] # first 20 ele
            default_url = see_all_link.split('/')[2]

            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))


            offset = 20
            gm_request_id = ['df3ef585-3d25-41a1-9849-30ad5e2a045d', 'a028cd40-8eaa-44b3-ac04-ec8730e4b185',
                             '9b013d1c-d93e-449b-a537-e27f9433f6e8', 'a4f98b55-457e-4297-a21c-d0340b1c43fa']
            index = 0
            while(True):
                index +=1
                requst_url = 'https://gateway.gofundme.com/web-gateway/v1/feed/'+ self.default_url + '/donations?limit=20&offset='+str(offset)+'&sort=recent'
                headers = {
                    'authority': 'gateway.gofundme.com',
                    'method': 'GET',
                    'path': '/web-gateway/v1/feed/'+self.default_url+'/donations?limit=20&offset='+str(offset)+'&sort=recent',
                    'scheme': 'https',
                    'accept': 'application/json, text/plain, */*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en,zh-HK;q=0.9,zh-TW;q=0.8,zh;q=0.7,en-US;q=0.6',
                    'cookie': 'gdid=00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc; optimizelyEndUserId=oeu1634762242824r0.41456249686518243; _gcl_au=1.1.1139821534.1634762244; _ga=GA1.2.1608920426.1634762244; _fbp=fb.1.1634762244815.673752098; _gcl_aw=GCL.1634781192.CjwKCAjw_L6LBhBbEiwA4c46ujKT2I6SoAPvbHeYZGGo6xeTAqVElh4SwuSClrWXCmtxjmeZvF3pjxoCaIIQAvD_BwE; _gac_UA-5577581-4=1.1634781193.CjwKCAjw_L6LBhBbEiwA4c46ujKT2I6SoAPvbHeYZGGo6xeTAqVElh4SwuSClrWXCmtxjmeZvF3pjxoCaIIQAvD_BwE; suid=664f511aeee745a888cd245e3fc9fa04; _gid=GA1.2.1103479206.1635107437; visitor=%7B%22locale%22%3A%22en_US%22%2C%22shimLocale%22%3A%22en_US%22%2C%22country%22%3A%22US%22%2C%22cookieWarning%22%3A%220%22%7D; optmzly_flow=cc_ssr_deferred_susi:variant; mp_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoiZ29mdW5kbWUtZmFzdHRyYWNrIiwiaW5wdXRMYWJlbCI6Ik1vYmlsZV9TREsiLCJpbnB1dFR5cGUiOiJKU1NESyJ9.VcK4Qu7IFdx-4eaNvFpO6-k7uLU4BnnoCaUKfLDYXBM_mixpanel=%7B%22distinct_id%22%3A%20%2200-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc%22%2C%22user_agent%22%3A%20%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F95.0.4638.54%20Safari%2F537.36%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%7D; mp_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoiZ29mdW5kbWUtZmFzdHRyYWNrIiwiaW5wdXRMYWJlbCI6ImpzX2ltcHJlc3Npb25zIiwiaW5wdXRUeXBlIjoiSlNTREsifQ.b5cv2xeiayTkWNVbv-Hg9BGILIHwgE1nL2Tl2OaPVIA_mixpanel=%7B%22distinct_id%22%3A%20%2200-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc%22%2C%22user_agent%22%3A%20%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F95.0.4638.54%20Safari%2F537.36%22%7D; mp_default__c=47; mp_default__c3=67783; mp_default__c4=61376; mp_default__c5=359; mp_impression__c=47; mp_impression__c3=67783; mp_impression__c4=61376; mp_impression__c5=359; amplitude_id_dec4ad7da36c150f9fffce4f288058a8gofundme.com=eyJkZXZpY2VJZCI6IjAwLTMxNjU4YjMwM2E3YTRiZGM4MzljMjRlOTY2MmQ5ZWUyLWFlMGRhOGJjIiwidXNlcklkIjpudWxsLCJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOjE2MzUyODAxNDYzNjEsImxhc3RFdmVudFRpbWUiOjE2MzUyODI2MDUzNTQsImV2ZW50SWQiOjg3LCJpZGVudGlmeUlkIjo0Niwic2VxdWVuY2VOdW1iZXIiOjEzM30=; ssid1=2613077abb-6e72b579d2c94583-b%3A1635284404; ssid2=2611fff167-988491df12c14ed7-4%3A1635455404; _ga_WF86BFEZ5L=GS1.1.1635280147.10.1.1635282606.39',
                    'gfm-request-id': gm_request_id[index % 4],
                    'origin': 'https://www.gofundme.com',
                    'referer': 'https://www.gofundme.com/',
                    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': "Windows",
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
                }
                result = s.get(requst_url, headers=headers, verify=cafile, timeout=5)
                # result = requests.get(requst_url, headers=headers, verify=cafile, timeout=5)
                time.sleep(1)
                if result.status_code != 200:
                    break  #some return 404 figure it out
                else:
                    result = json.loads(result.text)
                    offset += 20
                    donation_list += result['references']['donations']
                    if not result['meta']['has_next']:
                        break

            # print(donation_list)

            return donation_list

        except Exception as e:
            logging.exception(e)

    def getCounting(self):
        try:
            requst_url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + self.default_url+'/counts'
            headers = {
                'authority': 'gateway.gofundme.com',
                'method': 'GET',
                'path': '/web-gateway/v1/feed/' + self.default_url + '/counts',
                'scheme': 'https',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en,zh-HK;q=0.9,zh-TW;q=0.8,zh;q=0.7,en-US;q=0.6',
                'cookie': 'gdid=00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc; optimizelyEndUserId=oeu1634762242824r0.41456249686518243; _gcl_au=1.1.1139821534.1634762244; _ga=GA1.2.1608920426.1634762244; _fbp=fb.1.1634762244815.673752098; _gcl_aw=GCL.1634781192.CjwKCAjw_L6LBhBbEiwA4c46ujKT2I6SoAPvbHeYZGGo6xeTAqVElh4SwuSClrWXCmtxjmeZvF3pjxoCaIIQAvD_BwE; _gac_UA-5577581-4=1.1634781193.CjwKCAjw_L6LBhBbEiwA4c46ujKT2I6SoAPvbHeYZGGo6xeTAqVElh4SwuSClrWXCmtxjmeZvF3pjxoCaIIQAvD_BwE; suid=664f511aeee745a888cd245e3fc9fa04; _gid=GA1.2.1103479206.1635107437; visitor={"locale":"en_US","shimLocale":"en_US","country":"US","cookieWarning":"0"}; optmzly_flow=cc_ssr_deferred_susi:variant; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; mp_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoiZ29mdW5kbWUtZmFzdHRyYWNrIiwiaW5wdXRMYWJlbCI6Ik1vYmlsZV9TREsiLCJpbnB1dFR5cGUiOiJKU1NESyJ9.VcK4Qu7IFdx-4eaNvFpO6-k7uLU4BnnoCaUKfLDYXBM_mixpanel={"distinct_id": "00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc","user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","$initial_referrer": "https://www.google.com/","$initial_referring_domain": "www.google.com"}; mp_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoiZ29mdW5kbWUtZmFzdHRyYWNrIiwiaW5wdXRMYWJlbCI6ImpzX2ltcHJlc3Npb25zIiwiaW5wdXRUeXBlIjoiSlNTREsifQ.b5cv2xeiayTkWNVbv-Hg9BGILIHwgE1nL2Tl2OaPVIA_mixpanel={"distinct_id": "00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc","user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}; mp_default__c=64; mp_default__c3=90541; mp_default__c5=492; mp_default__c4=82351; mp_impression__c=64; mp_impression__c4=82351; mp_impression__c3=90541; mp_impression__c5=492; ssid1=261327278c-aaa4a31b3de04a7d-8:1635302703; ssid2=2611fff167-988491df12c14ed7-4:1635473703; _ga_WF86BFEZ5L=GS1.1.1635300904.12.0.1635300907.57; amplitude_id_dec4ad7da36c150f9fffce4f288058a8gofundme.com=eyJkZXZpY2VJZCI6IjAwLTMxNjU4YjMwM2E3YTRiZGM4MzljMjRlOTY2MmQ5ZWUyLWFlMGRhOGJjIiwidXNlcklkIjpudWxsLCJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOjE2MzUzMDA5MDgyMjcsImxhc3RFdmVudFRpbWUiOjE2MzUzMDA5MDgyMjYsImV2ZW50SWQiOjg3LCJpZGVudGlmeUlkIjo1MCwic2VxdWVuY2VOdW1iZXIiOjEzN30=',
                'origin': 'https://www.gofundme.com',
                'referer': 'https://www.gofundme.com/',
                'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "Windows",
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
            }
            result = requests.get(requst_url, headers=headers, verify=cafile, timeout=5)
            time.sleep(5)
            if result.status_code != 200:
                return None
            else:
                result = json.loads(result.text)
                counting = {
                    'counts': result['references']['counts'],
                    'updated_time': result['meta']['last_updated_at']
                }

                self.comment_counts = result['references']['counts']['total_comments']

                return counting
        except Exception as e:
            logging.exception(e)

    def getComment(self):
        try:
            comment_count = self.comment_counts
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))

            offset = 0
            gm_request_id = ['356340f9-b7c3-4857-ae8b-1bbbc694fe74', 'a028cd40-8eaa-44b3-ac04-ec8730e4b185',
                             '9b013d1c-d93e-449b-a537-e27f9433f6e8', 'a4f98b55-457e-4297-a21c-d0340b1c43fa']
            index = 0
            comments_list = []
            while (True):
                index += 1
                requst_url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + self.default_url + '/comments?limit=10&offset=' + str(offset)
                headers = {
                    'authority': 'gateway.gofundme.com',
                    'method': 'GET',
                    'path': '/web-gateway/v1/feed/' + self.default_url + '/comments?limit=10&offset=' + str(offset),
                    'scheme': 'https',
                    'accept': 'application/json, text/plain, */*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en,zh-HK;q=0.9,zh-TW;q=0.8,zh;q=0.7,en-US;q=0.6',
                    'cookie': 'gdid=00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc; optimizelyEndUserId=oeu1634762242824r0.41456249686518243; _gcl_au=1.1.1139821534.1634762244; _ga=GA1.2.1608920426.1634762244; _fbp=fb.1.1634762244815.673752098; suid=f28a58df2a2a4ce3859be0168a334e7a; _gcl_aw=GCL.1635641566.CjwKCAjw2vOLBhBPEiwAjEeK9tBORqcwfqF50YyPUHVUggUK1t9Ep6-eDJdqf49vVsrj-vwfE2Wc8RoCD5oQAvD_BwE; visitor={"locale":"en_US","shimLocale":"en_US","country":"US","cookieWarning":"0"}; _gac_UA-5577581-4=1.1635641567.CjwKCAjw2vOLBhBPEiwAjEeK9tBORqcwfqF50YyPUHVUggUK1t9Ep6-eDJdqf49vVsrj-vwfE2Wc8RoCD5oQAvD_BwE; optmzly_flow=cc_ssr_deferred_susi:variant; _gid=GA1.2.1781634118.1635759056; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; mp_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoiZ29mdW5kbWUtZmFzdHRyYWNrIiwiaW5wdXRMYWJlbCI6Ik1vYmlsZV9TREsiLCJpbnB1dFR5cGUiOiJKU1NESyJ9.VcK4Qu7IFdx-4eaNvFpO6-k7uLU4BnnoCaUKfLDYXBM_mixpanel={"distinct_id": "00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc","user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","$initial_referrer": "https://www.google.com/","$initial_referring_domain": "www.google.com"}; mp_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoiZ29mdW5kbWUtZmFzdHRyYWNrIiwiaW5wdXRMYWJlbCI6ImpzX2ltcHJlc3Npb25zIiwiaW5wdXRUeXBlIjoiSlNTREsifQ.b5cv2xeiayTkWNVbv-Hg9BGILIHwgE1nL2Tl2OaPVIA_mixpanel={"distinct_id": "00-31658b303a7a4bdc839c24e9662d9ee2-ae0da8bc","user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}; mp_default__c=1; mp_default__c5=11; mp_default__c4=2123; mp_default__c3=2286; mp_impression__c5=11; mp_impression__c4=2123; mp_impression__c3=2286; mp_impression__c=1; _gat_UA-5577581-4=1; _ga_WF86BFEZ5L=GS1.1.1635782155.28.1.1635783826.60; _dc_gtm_UA-5577581-4=1; ssid1=2616057c52-b6dbfaba699b4d7a-5:1635785627; ssid2=26152ef5a3-8533bf5bd4c94261-4:1635956627; amplitude_id_dec4ad7da36c150f9fffce4f288058a8gofundme.com=eyJkZXZpY2VJZCI6IjAwLTMxNjU4YjMwM2E3YTRiZGM4MzljMjRlOTY2MmQ5ZWUyLWFlMGRhOGJjIiwidXNlcklkIjpudWxsLCJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOjE2MzU3ODIxNTQ5NTMsImxhc3RFdmVudFRpbWUiOjE2MzU3ODM4NDc0OTQsImV2ZW50SWQiOjE1NCwiaWRlbnRpZnlJZCI6OTcsInNlcXVlbmNlTnVtYmVyIjoyNTF9',
                    'gfm-request-id': gm_request_id[index % 4],
                    'origin': 'https://www.gofundme.com',
                    'referer': 'https://www.gofundme.com/',
                    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': "Windows",
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
                }
                result = s.get(requst_url, headers=headers, verify=cafile, timeout=5)
                # result = requests.get(requst_url, headers=headers, verify=cafile, timeout=5)
                time.sleep(1)
                if result.status_code != 200:
                    break
                else:
                    result = json.loads(result.text)
                    offset += 10
                    for i in result['references']['contents']:
                        comment = {"comment_id": i['comment']['comment_id'],
                                   "name": i['donation']['name'],
                                   "created_time": i['comment']['timestamp'],
                                   "content": i['comment']['comment'],
                                   "donation_amount": i['donation']['amount'],
                                   "is_anonymous": i['donation']['is_anonymous']}
                        comments_list.append(comment)
                    if not result['meta']['has_next']:
                        break
                    if len(comments_list) >= comment_count:
                        break

            return comments_list

        except Exception as e:
            logging.exception(e)

    def extractor(self):
        info = {'url': self.url,
                'collected_date': self.getCollectedDate(),
                'created_date': self.getCreatedDate(),
                'campaign_name': self.getCampaignName(),
                'location': self.getLocation(),
                'fundraising_team': self.getFundraisingTeam(),
                'beneficiary': self.getBeneficiary(),
                'description': self.getDescription(),
                'donation': self.getDonationInfo(),
                'counting': self.getCounting(),
                'comment': self.getComment(),
                # 'update': self.getUpdate(),
                'donation_list': self.getDonationList(),
                }

        return info


if __name__ == '__main__':
    try:
        # example
        extractor = IndividualPageInfoExtractor('https://www.gofundme.com/f/randall-smiths-funeral-childrens-future-fund')
        info_dict = extractor.extractor()
        with open('data/fullcircle.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(info_dict, indent=4, separators=(',', ':')))
        # print(info_dict)
    except Exception as e:
        logging.exception(e)

