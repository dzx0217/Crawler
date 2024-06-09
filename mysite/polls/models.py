import datetime
from django.db import models
from django.utils import timezone 

# Create your models here.

class Question(models.Model):
	question_text = models.CharField(max_length=200)# 问题
	pub_date = models.DateTimeField("date published")# 发表时期

	def __str__(self):
		return self.question_text
	
	def was_published_recently(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
	question = models.ForeignKey(Question,on_delete=models.CASCADE)# 关联一个问题
	choice_text = models.CharField(max_length=200)# 选项
	votes = models.IntegerField(default=0)# 投票结果

	def __str__(self):
		return self.choice_text
	