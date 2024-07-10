# content/views.py
from django.shortcuts import render
from .models import Article

def article_detail(request):
    article = Article.objects.first()
    return render(request, 'content/article_detail.html', {'article': article})