from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CallBegin(models.Model):
    client_number = models.CharField(max_length=20, null=False, blank=False, verbose_name="Номер клиента")
    client = models.ForeignKey(User, related_name="clients", db_column="client",null=True, on_delete=models.PROTECT, verbose_name="Клиент")
    manager_number = models.CharField(max_length=20, null=False, blank=False, verbose_name="Номер менеджера")
    manager = models.ForeignKey(User, related_name="managers",db_column="manager",null=True, on_delete=models.PROTECT, verbose_name="Менеджер")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.client.username if self.client != None else "Неизвестный"} ({self.client_number}) -> {self.manager.username if self.manager != None else ""} ({self.manager_number})"
    
    class Meta:
        verbose_name = "Входящий звонок"
        verbose_name_plural = "Входящие звонки"
        ordering = ['created_at']