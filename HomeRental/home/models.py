from django.db import models
from django.contrib.auth.models import User 
# Create your models here.

class home(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=200)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Property(models.Model):
    PROPERTY_TYPE =(
        ('rent','Rent'),
        ('sell','Sell')

    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE)
    image= models.ImageField(upload_to='property_images/')
    created_at= models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_bookings")
    booked_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

   

    def __str__(self):
        return f'{self.user.username}- {self.title}'
    
