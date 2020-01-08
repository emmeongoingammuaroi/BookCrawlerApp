import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from .models import Book
from .models import Query
import multiprocessing


class Books:
	def __init__(self, title, price, content, url, image, price_int):
		self.title = title
		self.price = price
		self.content = content
		self.url = url
		self.image = image
		self.price_int = price_int


def convert(a):
	b = list(a)
	for i in range(len(b)):
		if b[i] == ' ':
			b[i] = '+'
	return  ''.join(b)

class Crawler:
	def getTiki(self, url):
		try:
			req = requests.get(url)
		except:
			return None
		return BeautifulSoup(req.text, 'html.parser')

	def getFahasa(self, url):
		my_headers = {
	        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
				        AppleWebKit/537.36 ' + ' (KHTML, like Gecko)\
				        Chrome/61.0.3163.100 Safari/537.36'
		}
		req = requests.post(url, headers = my_headers)
		return BeautifulSoup(req.text, 'html.parser')

	def safeGet(self, pageObj, selector):
		childObj = pageObj.select(selector)
		if childObj is not None and len(childObj) > 0:
			return childObj[0].get_text()
		return ""

	def crawlerTiki(self, topic, results):
		print("TIKI RUNNING...")
		topic_convert = convert(topic)
		bs = self.getTiki('https://tiki.vn/search?q='+ topic_convert)
		searchResults = bs.select('div.product-item')
		for result in searchResults:
			try:
				url = result.select('a')[0].attrs['href']
			except:
				break
			bs = self.getTiki(url)
			if bs is None:
				break
			title = self.safeGet(bs, 'h1.item-name')
			title1 = unidecode(title)
			if topic not in title1.lower():
				break
			price = self.safeGet(bs, 'span#span-price')
			price_int = int(price[:-1].replace('.',''))
			content = self.safeGet(bs, 'div#gioi-thieu')
			image = bs.select('img.product-magiczoom')[0].attrs['src']
			book = Books(title, price, content, url, image, price_int)
			results.append(book)

		return results


	def crawlerFahasa(self, topic, results):
		print('FAHASA RUNNING...')
		topic_convert = convert(topic)
		bs = self.getFahasa('https://www.fahasa.com/catalogsearch/result/?q=' + topic_convert)
		search = bs.find_all('h2', {'class':"product-name p-name-list"})
		for result in search:
			try:
			    url = result.select('a')[0].attrs["href"]
			except:
				break
			bs = self.getFahasa(url)
			if bs is None:
				break
			title = self.safeGet(bs, 'h1')
			content = self.safeGet(bs, 'div#product_tabs_description_contents')
			price = bs.find_all('span',{'class':'price'})[1].get_text().strip()
			price_int = int(price[:-2].replace('.', ''))
			image = bs.find('img',{'class':'fhs-p-img'}).attrs['src']
			book = Books(title, price, content, url, image, price_int)
			results.append(book)

		return results

def crawlerBook(id_query):
	query = Query.objects.get(id=id_query)
	print("QUERY", query)
	topic = query.search
	print("TIM KIEM: ", topic)
	crawler = Crawler()
	results1 = multiprocessing.Manager().list([])
	results2 = multiprocessing.Manager().list([])
	process1 = multiprocessing.Process(target=crawler.crawlerTiki, args=(topic, results1))
	process2 = multiprocessing.Process(target=crawler.crawlerFahasa, args=(topic, results2))
	process1.start()
	process2.start()
	process1.join()
	process2.join()
	results1.extend(results2)
	price_list = [book.price_int for book in results1 ]
	price_top8 = sorted(price_list)[0:8]
	#danh sach 5 cuon gia re nhat
	result_top8 = [book for book in results1 if book.price_int in price_top8]
	#append vao database
	for book in result_top8:
		print("NEW BOOK: ", book)
		Book.objects.create(title=book.title,
			                image_url=book.image,
			                description=book.content,
			                link=book.url,
			                price_int=book.price_int,
			                price=book.price,
			                query=query)

