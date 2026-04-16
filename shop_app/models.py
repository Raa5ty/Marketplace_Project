from django.db import models

# Create your models here.

class Product(models.Model):
    """
    Модель товара для интернет-магазина.
    """
    # Название товара (максимум 255 символов)
    name = models.CharField(
        max_length=255,
        verbose_name="Название товара",
        help_text="Введите название товара"
    )
    
    # Описание товара (текстовое поле, может быть большим)
    description = models.TextField(
        verbose_name="Описание",
        help_text="Подробное описание товара",
        blank=True  # может быть пустым
    )
    
    # Цена товара (максимум 10 цифр, 2 знака после запятой)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Цена товара в рублях"
    )
    
    # Изображение товара (загружается в папку products/)
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Изображение",
        help_text="Загрузите изображение товара",
        blank=True,
        null=True
    )
    
    # Дата создания (автоматически проставляется при создании)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']  # сортировка по дате создания (сначала новые)
    
    def __str__(self):
        """Строковое представление товара (для админки)"""
        return self.name