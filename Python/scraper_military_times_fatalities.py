# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------#
# Pull Military Times Fatality Data
#-----------------------------------------------------------------------------#

# import modules an custom function
import pandas
import scrapy.selector
import urllib2
import re

def fill_list(l):
    if not l:
        l = ['NaN']
    return l
        
def extract_service(x):
    return re.sub("^(\\w+).*", "\\1", x)

def extract_rank(x):
    return re.sub("^\\w+\\s+(.+?)\\..*", "\\1", x)
            
def remove_rank(x):
    return re.sub("^(.+?)\\.\\s+|^\\s+|\\s+$", "", x)

# define xpath expressions
mt_fatal = "http://projects.militarytimes.com/valor/search?conflict=1+2+3"
name_xpath = '//div[@class="data-box-right"]/h3[1]/a/text()'
date_xpath = '//div[@class="data-box-right"]/span/text()'
summ_xpath = '//div[@class="data-box-right"]/text()'
link_xpath = '//div[@class="data-box-right"]/h3/a[1]/@href'
op_xpath = '//div[@class="record-txt"]/h2/text()'
age_xpath = '//div[@class="record-txt"]/text()'
orig_xpath = '//div[@class="record-txt"]/text()'
assign_xpath = '//div[@class="record-txt"]/text()'
full_xpath = '//div[@class="record-txt"]/text()'

# read page source
html_response = urllib2.urlopen(mt_fatal).read()
hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

last_page_xpath = "".join(
    '//div[@class="number-block"]/form/ul/li[a = "Last"]/a[@href]/@href')
last_page = hsx.select(last_page_xpath).extract()
last_page = int(re.search("\\d+$", last_page[0]).group())

mt_fatal_df = pandas.DataFrame()

# loop through each page
for i in range(1, last_page): 
    #print(str(round((i/last_page)*100, 1)) + '%')
    print(i)
    
    html_response = urllib2.urlopen(mt_fatal + "&page=" + str(i)).read()
    html_response = re.sub('\\r|\\n|\\t|\\(|\\)', "", html_response)
    html_response = re.sub('>:?\\s+<', "><", html_response)
    html_response = re.sub('^\\s+|\\s+$|(?<=\\s)\\s+', "", html_response)
    html_response = re.sub(
        '(<h3 class="h3-size"><a.*?\\d+">)\\s*(</a></h3>)',
        '\\1NaN\\2',
        html_response)
    
    hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

    page_name = hsx.select(name_xpath).extract()
    page_date = hsx.select(date_xpath).extract()
    page_summ = hsx.select(summ_xpath).extract()
    page_link = hsx.select(link_xpath).extract()    
    page_service = map(extract_service, page_name)    
    page_rank = map(extract_rank, page_name)        
    page_name = map(remove_rank, page_name)

    page_full = []
    page_op = []
    page_age = []
    page_orig = []
    page_assign = []

    # loop through each link on page
    for x in page_link:
        print(x)
        html_response = urllib2.urlopen(str(x)).read()
        html_response = re.sub('\\r|\\n|\\t|\\(|\\)', "", html_response)
        html_response = re.sub('<p>|</p>', "", html_response)
        html_response = re.sub('>:?\\s+<', "><", html_response)
        html_response = re.sub('^\\s+|\\s+$|(?<=\\s)\\s+|(?<=>)\\s+', 
                               "", html_response)
        
        hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

        op_select = hsx.select(op_xpath).re("(?<=During ).*")
        op_select = fill_list(op_select)
        page_op.append(op_select.pop())
                
        age_select = hsx.select(age_xpath).re("^\\d+")
        age_select = fill_list(age_select)
        page_age.append(age_select.pop())
        
        orig_select = hsx.select(orig_xpath).re(
            "^\\d+,\\s*of\\s+(.*?,\\s+.*?)\\.?(?=;|,)")
        orig_select = fill_list(orig_select)
        page_orig.append(orig_select.pop())
        
        assign_select = hsx.select(assign_xpath).re(
            "^\\d+.*?(;|,)\\s+.?(assigned\\s+to|member\\s+of)\\s+(.*?)(?=;|,)")
        assign_select = fill_list(assign_select)
        page_assign.append(assign_select.pop())
        
        full_select = hsx.select(full_xpath).extract()
        full_select = fill_list(full_select)
        page_full.append(full_select.pop())

    mt_fatal_df = mt_fatal_df.append(
        pandas.DataFrame({
            'name' : page_name, 
            'age' : page_age,
            'origin' : page_orig,
            'date' : page_date,
            'operation' : page_op,
            'rank' : page_rank,
            'service' : page_service,
            'assignment' : page_assign,            
            'summary' : page_summ,
            'full_text' : page_full,
            'link' : page_link,
            },
            columns = ['name', 'age', 'origin', 'date', 'operation', 'rank', 
                       'service', 'assignment', 'summary', 'full_text', 
                       'link']))
