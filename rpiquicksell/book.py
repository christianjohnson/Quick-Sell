import xml.dom.minidom

def getText(nodelist):
  rc = []
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      rc.append('%s'%node.data)
  return ''.join(rc)

class StorePrice:
  def __init__(self, PriceData):
    self.url = PriceData.getAttribute('store_url')
    self.storeID = PriceData.getAttribute('store_id')
    self.currencyCode = PriceData.getAttribute('currency_code')
    self.inStock = PriceData.getAttribute('is_in_stock')
    self.isNew = PriceData.getAttribute('is_new')
    self.isHistoric = PriceData.getAttribute('is_historic')
    self.checkTime = PriceData.getAttribute('check_time')
    self.price = float(PriceData.getAttribute('price'))
    self.currencyRate = float(PriceData.getAttribute('currency_rate'))
  
  def __str__(self):
    return """
    url %s
    storeid %s
    currencyCode %s
    inStock %s
    isNew %s
    isHistoric %s
    checkTime %s
    price %s
    currencyRate %s
    """%(self.url,self.storeID,self.currencyCode,self.inStock,self.isNew,self.isHistoric,self.checkTime,self.price,self.currencyRate)

class Book:
  def __init__(self, BookData):
    print(BookData.toxml())
    self.title = getText(BookData.getElementsByTagName("Title")[0].childNodes)
    self.titleLong = getText(BookData.getElementsByTagName("TitleLong")[0].childNodes)
    self.authorsText = getText(BookData.getElementsByTagName("AuthorsText")[0].childNodes)
    self.publisherText = getText(BookData.getElementsByTagName("PublisherText")[0].childNodes)
    self.summary = getText(BookData.getElementsByTagName("Summary")[0].childNodes)
    self.notes = getText(BookData.getElementsByTagName("Notes")[0].childNodes)
    self.urlText = getText(BookData.getElementsByTagName("UrlsText")[0].childNodes)
    price_list = BookData.getElementsByTagName('Price');
    self.prices = []
    for price in price_list:
      self.prices.append(StorePrice(price))
  
  def __str__(self):
    ret = """title %s
longTitle %s
authors %s
publisher %s
summary %s
notes %s
url %s"""%(self.title,self.titleLong,self.authorsText,self.publisherText,self.summary,self.notes,self.urlText)
    ret+='\nprices\n'
    for price in self.prices:
      ret+=str(price)
    return ret
