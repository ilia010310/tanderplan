from tasks import collect_links


url1 = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1'
url2 = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=2'
collect_links.delay(url1)
collect_links.delay(url2)




