import xml.dom.minidom


def getText(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append('%s'%node.data)
	return ''.join(rc)

def parseFile(file):
	return handleDocument(xml.dom.minidom.parse(file))

def parseString(string):
	return handleDocument(xml.dom.minidom.parseString(file))

def handleDocument(document):
	return handleBooks(document.getElementsByTagName("BookData"))

def handleBooks(books):
	rc = []
	for book in books:
		rc.append(handleBook(book))
	return rc

def handleBook(book):
	rc = {}
	rc['Title'] = getText(book.getElementsByTagName("Title")[0].childNodes)
	rc['TitleLong'] = getText(book.getElementsByTagName("TitleLong")[0].childNodes)
	rc['AuthorsText'] = getText(book.getElementsByTagName("AuthorsText")[0].childNodes)
	rc['PublisherText'] = getText(book.getElementsByTagName("PublisherText")[0].childNodes)
	return rc
