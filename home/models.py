from django.db import models

# Create your models here.

class SingletonModel:
	'''
	Singleton model
	Only one model instance exists
	'''
	def save(self, *args, **kwargs):
		if self.pk == None and self.__class__.objects.all().count() > 0:
			return None
		return super().save(*args, **kwargs)

	@classmethod
	def get_instance(cls):
		if cls.has_object():
			return cls.objects.first()
		return cls()

	@classmethod
	def has_object(cls):
		return cls.objects.all().count() > 0

class BackgroundImage(SingletonModel, models.Model):
	photo = models.ImageField(upload_to='backgrounds', null=True, blank=True)

	def get_photo(self):
		if self.photo:
			return self.photo.url
		return '/static/home/assets/image/lumbini-background.jpg'