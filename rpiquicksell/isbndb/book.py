import xml.dom.minidom

class StoreData:
  def __init__(self,url,storeId):
    self.url = url
    self.storeId = storeId

  def __str__(self):
    return "url: %s\nstore: %s"%(self.url,self.storeId)

class CostInUSD:
  def __init__(self,currencyCode,price,currencyRate):
    self.orig_currency = currencyCode
    self.usdprice = float(price)*float(currencyRate)
  
  def __str__(self):
    return "original Currency: %s\n price: %f"%(self.orig_currency,self.usdprice)

class StockData:
  def __init__(self, inStock, isNew):
    self.inStock = inStock
    self.isNew = isNew
  
  def __str__(self):
    return "in stock? "+str(self.inStock)+"\n new? "+str(self.isNew)

class SiteData:
  def __init__(self, checkTime, isHistoric):
    self.checkTime = checkTime
    self.isHistoric = isHistoric

  def __str__(self):
    return "check time: "+str(self.checkTime)+"\nHistoric? "+str(self.isHistoric)


class StockSiteData:
  def __init__(self,inStock,isNew,checkTime,isHistoric):
    self.site = SiteData(checkTime,isHistoric)
    self.stock = StockData(inStock,isNew)
  def __str__(self):
    return "%s\n%s"%(str(self.site),str(self.stock))

class StoreCostData:
  def __init__(self,url,storeId,currencyCode,price,currencyRate):
    self.store = StoreData(url,storeId)
    self.cost = CostInUSD(currencyCode,price,currencyRate)

  def __str__(self):
    return "%s\n%s"%(str(self.store),str(self.cost))

class StorePrice:
  def __init__(self, StockSiteData, StoreCostData):
    self.stockSiteData = StockSiteData
    self.storeCostData = StoreCostData
  
  def __str__(self):
    return "%s\n%s"%(str(self.stockSiteData),str(self.storeCostData))


class PartyData:
  def __init__(self,authors,publisher):
    self.authors = authors
    self.publisher = publisher
  
  def __str__(self):
    return "authors: %s\npublisher: %s"%(self.authors,self.publisher)

class TitleData:
  def __init__(self,title,titleLong):
    self.title = title.strip()
    self.titleLong = titleLong

  def __str__(self):
    if(self.titleLong):
      return 'title: '+self.titleLong
    return 'title: '+self.title

class PublicationData:
  def __init__(self,title,titlelong,authorsText,publisherText):
    self.titleData = TitleData(title,titlelong)
    self.partyData = PartyData(authorsText,publisherText)

  def __str__(self):
    return str(self.titleData)+"\n"+str(self.partyData)

class BookURL:
  def __init__(self, url):
    self.url = url

  def __str__(self):
    return "url: %s"%(self.url)

class BookInfoData:
  def __init__(self,summary,notes):
    self.summary = summary
    self.notes = notes

  def __str__(self):
    return "Summary: %s\nNotes: %s"%(self.summary, self.notes)

class BookInfo:
  def __init__(self,summary,notes,urltext):
    self.infoData = BookInfoData(summary,notes)
    self.url = BookURL(urltext)
  
  def __str__(self):
    return "%s\n%s"%(str(self.infoData), str(self.url))

class BookData:
  def __init__(self,info,publication):
    self.info = info
    self.publication = publication

  def __str__(self):
    return "%s\n%s"%(str(self.info),str(self.publication))

class Book:
  def __init__(self, BookData, prices):
    self.BookData = BookData
    self.Prices = prices

  def __str__(self):
    stringval = str(self.BookData)+'\n====='
    stringval += '\n=====\n'.join([str(price) for price in self.Prices])
    return stringval

class PriceXMLParser:
  def parse(self, PriceData):
    url = PriceData.getAttribute('store_url')
    storeID = PriceData.getAttribute('store_id')
    currencyCode = PriceData.getAttribute('currency_code')
    inStock = bool(int(PriceData.getAttribute('is_in_stock')))
    isNew = bool(int(PriceData.getAttribute('is_new')))
    isHistoric = bool(int(PriceData.getAttribute('is_historic')))
    checkTime = PriceData.getAttribute('check_time')
    price = float(PriceData.getAttribute('price'))
    currencyRate = float(PriceData.getAttribute('currency_rate'))
    
    stockSiteData = StockSiteData(inStock,isNew,checkTime,isHistoric)
    storeCostData = StoreCostData(url,storeID,currencyCode,currencyRate,price)

    return StorePrice(stockSiteData,storeCostData)

class BookXMLParser:
  def __init__(self, priceParser=None):
    self.priceParser = priceParser
    if not self.priceParser:
      self.priceParser = PriceXMLParser()
    
  def parse(self, bookData):
    title = self.getText(bookData.getElementsByTagName("Title")[0].childNodes)
    longTitle = self.getText(bookData.getElementsByTagName("TitleLong")[0].childNodes)
    authorsText = self.getText(bookData.getElementsByTagName("AuthorsText")[0].childNodes)
    publishersText = self.getText(bookData.getElementsByTagName("PublisherText")[0].childNodes)
    summary = self.getText(bookData.getElementsByTagName("Summary")[0].childNodes)
    notes = self.getText(bookData.getElementsByTagName("Notes")[0].childNodes)
    urlText = self.getText(bookData.getElementsByTagName("UrlsText")[0].childNodes)
    
    publicationData = PublicationData(title,longTitle,authorsText,publishersText)
    bookInfo = BookInfo(summary,notes,urlText)
    bookDataObj = BookData(publicationData,bookInfo)


    pricesData = bookData.getElementsByTagName('Price')
    priceList = []

    for priceData in pricesData:
      price = self.priceParser.parse(priceData)
      priceList.append(price)
    
    book = Book(bookDataObj,priceList)
    return book

  def getText(self,nodelist):
    rc = []
    for node in nodelist:
      if node.nodeType == node.TEXT_NODE:
        rc.append('%s'%node.data)
    return ''.join(rc)




