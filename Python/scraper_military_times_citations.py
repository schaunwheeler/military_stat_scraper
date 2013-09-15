# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------#
# Pull Military Times Citation/Awards Data
#-----------------------------------------------------------------------------#

# import modules and define custom functions
import pandas
import scrapy.selector
import urllib2
import re

def fill_list(l):
    if not l:
        l = ['NaN']
    return l

# define xpath expressins        
mt_awards = "".join((
    "http://projects.militarytimes.com/citations-medals-awards/",
    "search.php?conflict=6"))
name_xpath = '//div[@class="data-box"]/h3[1]/a/text()'
award_xpath = '//div[@class="data-box"]/h3[last()]/a/text()'
date_xpath = '//div[@class="data-box"]/a/text()'
summ_xpath = '//div[@class="data-box"]/text()'
link_xpath = '//div[@class="data-box"]/a[last()]/@href'
op_xpath = ''.join((
    '//div[@class="grid_14"]/*[text()="Action Date: "]', 
    '/following::text()[1]'))
rank_xpath = ''.join((
    '//div[@class="grid_14"]/*[text()="Rank: "]', 
    '/following::text()[1]'))
service_xpath = ''.join((
    '//div[@class="grid_14"]/*[text()="Service: "]', 
    '/following::a/text()[1]'))
text_xpath = '//p[@class="line-h"]/text()'

# read page source
html_response = urllib2.urlopen(mt_awards).read()
hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

last_page_xpath = ''.join(
    '//div[@class="number-block"]/form/ul/li[a = "Last"]/a[@href]/@href')
last_page = hsx.select(last_page_xpath).extract()
last_page = int(re.search("\\d+$", last_page[0]).group())

mt_awards_df = pandas.DataFrame()

# loop through all pages
for i in range(1, last_page): 
    #print(str(round((i/last_page)*100, 1)) + '%')
    print(i)
    
    html_response = urllib2.urlopen(mt_awards + "&page=" + str(i)).read()
    html_response = re.sub('\\r|\\n|\\t|\\(|\\)', "", html_response)
    html_response = re.sub('>:?\\s+<', "><", html_response)
    html_response = re.sub('^\\s+|\\s+$|(?<=\\s)\\s+', "", html_response)
    html_response = re.sub(
        '(<h3 class="h3-size"><a.*?recipientid=\\d+">)\\s*(</a></h3>)',
        '\\1NaN\\2',
        html_response)
    html_response = re.sub(
        '(<b>Date.*?recipientid=\\d+">)\\s*(</a><br />)',
        '\\1NaN\\2',
        html_response)

    hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

    page_name = hsx.select(name_xpath).extract()
    page_award = hsx.select(award_xpath).extract()
    page_date = hsx.select(date_xpath).extract()
    page_summ = hsx.select(summ_xpath).extract()
    page_link = hsx.select(link_xpath).extract()

    page_text = []
    page_op = []
    page_rank = []
    page_service = []

    # loop through all links on page
    for x in page_link:
        print(x)
        html_response = urllib2.urlopen(str(x)).read()
        html_response = re.sub('\\r|\\n|\\t|\\(|\\)', "", html_response)
        html_response = re.sub('>:?\\s+<', "><", html_response)
        html_response = re.sub('^\\s+|\\s+$|(?<=\\s)\\s+', "", html_response)
        
        hsx = scrapy.selector.HtmlXPathSelector(text = html_response)

        op_select = hsx.select(op_xpath).extract()
        op_select = fill_list(op_select)
        page_op.append(op_select.pop())
                
        rank_select = hsx.select(rank_xpath).extract()
        rank_select = fill_list(rank_select)
        page_rank.append(rank_select.pop())
        
        service_select = hsx.select(service_xpath).extract()
        service_select = fill_list(service_select)
        page_service.append(service_select.pop())
        
        text_select = hsx.select(text_xpath).extract()
        service_select = fill_list(service_select)
        page_text.append(text_select.pop())

    mt_awards_df = mt_awards_df.append(
        pandas.DataFrame({
            'name' : page_name, 
            'award' : page_award,
            'date' : page_date,
            'operation' : page_op,
            'rank' : page_rank,
            'service' : page_service,
            'summary' : page_summ,
            'citation' : page_text,
            'link' : page_link,
            },
            columns = ['name', 'award', 'date', 'operation', 'rank', 'service',
                       'summary', 'citation', 'link']))
