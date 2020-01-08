from django.shortcuts import render
from .models import Book, Query
from .bookcrawler import crawlerBook
from django.utils.text import slugify


def search(request):
	search = False
	query = request.GET.get('q', None)
	books = None
	if query:
		search = True
		slug_of_query = slugify(query)
		slug_exist = Query.objects.filter(slug=slug_of_query).exists()
		q = Query.objects.get(slug=slug_of_query) if slug_exist else None
		if q:
			books = q.books.all()
			print("TIM THAY QUERY") 
		
		else:
			q = Query.objects.create(search=query)
			q.save()
			crawlerBook(q.id)

			books = q.books.all()

	context = {
	    'books': books,
	    'search': search
	}

	return render(request,
			    'book_list.html',
			    context)


