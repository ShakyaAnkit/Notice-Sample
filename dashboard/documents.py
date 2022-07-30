from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Notice

@registry.register_document
class NoticeDocument(Document):
	description = fields.TextField(attr="description")
	ministry = fields.IntegerField(attr="ministry")
	office = fields.IntegerField(attr="office")
	category = fields.IntegerField(attr="category")
	notice_date = fields.DateField(attr="notice_date")

	class Index:
		# Name of the Elasticsearch index
		name = 'notices'
		# See Elasticsearch Indices API reference for available settings
		settings = {'number_of_shards': 1,
					'number_of_replicas': 0}

	class Django:
		model = Notice # The model associated with this Document

		# The fields of the model you want to be indexed in Elasticsearch
		fields = [
			'title',
		]

		queryset_pagination = 50
	
	def prepare_ministry(self, instance):
		return instance.ministry.pk

	def prepare_office(self, instance):
		if instance.office:
			return instance.office.pk
		return None

	def prepare_category(self, instance):
		if instance.category:
			return instance.category.pk
		return None

'''
# USAGE

# Search object
search_result = NoticeDocument.search()

# All search
search_result = search_result.query('multi_match', query='ajesh test', )

# Normal Filter (eg. title)
search_result = search_result.filter('term', title='ajesh') # term match

# Exact match filter (eg. ministry pk filter)
search_result = search_result.query('match', ministry=1) # term match

# Date filter (eg. notice date)
search_result = search_result.query('range', **{'notice_date': {'gte': '2021-03-01'} })

# Queryset
search_result.to_queryset()

'''