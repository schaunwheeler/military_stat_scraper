# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------#
# Pull iCasualties data
#-----------------------------------------------------------------------------#

# import modules and custom functions
import pandas
import scrapy.selector
import urllib2
import re
import numpy
import selenium.webdriver
import time

def clean_icasualties_table(html_response):
    html_response = re.sub('\\r|\\n|\\t|\\(|\\)', "", html_response)
    html_response = re.sub('>:?\\s+<', "><", html_response)
    html_response = re.sub('^\\s+|\\s+$|(?<=\\s)\\s+|(?<=>)\\s+', 
                       "", html_response)
    html_response = re.sub('<tr\\s+.*?/tr>', "", html_response)
    html_response = re.sub(
        '<tr>(?=<td colspan).*?javascript.*/tr>(?=</table>)', 
        "", 
        html_response)
    return html_response

# read page source
html_response = urllib2.urlopen(
    'http://icasualties.org/OEF/Fatalities.aspx').read()
n_records = re.search(
    '(?<=>Records returned:\\s)\\d+(?=<)', 
    html_response).group()
n_records = int(n_records)

html_response = clean_icasualties_table(html_response)
hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

th_xpath = '//table[@id="ctl00_ContentPlaceHolder1_gvReport"]/tr/th/text()'
th = hsx.select(th_xpath).extract()

tr_xpath = '//table[@id="ctl00_ContentPlaceHolder1_gvReport"]/tr/td/text()'
tr = hsx.select(tr_xpath).extract()

n_records_per_page = len(tr) / len(th)
n_pages = int(numpy.ceil(n_records / n_records_per_page))

icas_df = pandas.DataFrame()

th_xpath = '//table[@id="ctl00_ContentPlaceHolder1_gvReport"]/tr/th/text()'
th = hsx.select(th_xpath).extract()

tr_xpath = '//table[@id="ctl00_ContentPlaceHolder1_gvReport"]/tr/td/text()'
tr = hsx.select(tr_xpath).extract()

icas_df = icas_df.append(
    pandas.DataFrame(
        numpy.array(tr).reshape((len(tr)/len(th),len(th))), 
        columns = th))

wd = selenium.webdriver.Firefox()

wd.get('http://icasualties.org/OEF/Fatalities.aspx')

time.sleep(5)

# loop through each page
for i in range(2, n_pages + 1):

    wd.execute_script(
        ''.join((
            "javascript:__doPostBack('ctl00$ContentPlaceHolder1$gvReport','Page$",
            str(i),
            "')")))
    
    time.sleep(5)
                           
    html_reponse = wd.page_source
    html_response = clean_icasualties_table(html_response)
    hsx = scrapy.selector.HtmlXPathSelector(text = html_response)
    
    th_xpath = '//table[@id="ctl00_ContentPlaceHolder1_gvReport"]/tr/th/text()'
    th = hsx.select(th_xpath).extract()
    
    tr_xpath = '//table[@id="ctl00_ContentPlaceHolder1_gvReport"]/tr/td/text()'
    tr = hsx.select(tr_xpath).extract()
    
    icas_df_temp = pandas.DataFrame(
            numpy.array(tr).reshape((len(tr)/len(th),len(th))), 
            columns = th)
            
    icas_df = icas_df.append(icas_df_temp)