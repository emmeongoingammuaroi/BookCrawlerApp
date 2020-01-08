from django.db import models
from django.utils.text import slugify

class Query(models.Model):
	search = models.CharField(max_length=200)
	slug = models.SlugField(blank=True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.search)
		return super(Query, self).save(*args, **kwargs)
		
	def __str__(self):
		return self.search



class Book(models.Model):
	title = models.CharField(max_length=200)
	image_url = models.URLField()
	description = models.TextField()
	link = models.URLField()
	price_int = models.PositiveIntegerField(default=0)
	price = models.CharField(max_length=200)
	query = models.ForeignKey('Query',
							on_delete=models.CASCADE,
							related_name='books')

	class Meta:
		ordering = ('price_int',)

	def __str__(self):
		return self.title

