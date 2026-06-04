from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image_url = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# 11 Domain-Specific Models
class Mobile(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='mobile_details')
    storage = models.CharField(max_length=50, null=True, blank=True)
    camera = models.CharField(max_length=50, null=True, blank=True)
    ram = models.CharField(max_length=50, null=True, blank=True)
    display = models.CharField(max_length=50, null=True, blank=True)
    battery = models.CharField(max_length=50, null=True, blank=True)
    design = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)

class Computer(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='computer_details')
    cpu = models.CharField(max_length=50, null=True, blank=True)
    gpu = models.CharField(max_length=50, null=True, blank=True)
    weight = models.CharField(max_length=50, null=True, blank=True)
    durability = models.CharField(max_length=100, null=True, blank=True)
    screen = models.CharField(max_length=50, null=True, blank=True)
    refresh_rate = models.CharField(max_length=50, null=True, blank=True)
    ram = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)

class Clothes(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='clothes_details')
    material = models.CharField(max_length=100, null=True, blank=True)
    fit = models.CharField(max_length=50, null=True, blank=True)
    style = models.CharField(max_length=50, null=True, blank=True)
    pattern = models.CharField(max_length=50, null=True, blank=True)
    pockets = models.IntegerField(null=True, blank=True)
    fabric = models.CharField(max_length=50, null=True, blank=True)
    luxury = models.BooleanField(null=True, blank=True)
    temp = models.CharField(max_length=50, null=True, blank=True)

class Shoes(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='shoes_details')
    cushion = models.CharField(max_length=50, null=True, blank=True)
    tech = models.CharField(max_length=50, null=True, blank=True)
    style = models.CharField(max_length=50, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    retro = models.BooleanField(null=True, blank=True)
    weight = models.CharField(max_length=50, null=True, blank=True)
    support = models.CharField(max_length=50, null=True, blank=True)

class Watches(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='watches_details')
    water = models.CharField(max_length=50, null=True, blank=True)
    shock = models.CharField(max_length=50, null=True, blank=True)
    movement = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)
    style = models.CharField(max_length=50, null=True, blank=True)
    lume = models.CharField(max_length=50, null=True, blank=True)
    iconic = models.BooleanField(null=True, blank=True)
    classic = models.BooleanField(null=True, blank=True)

class Cosmetics(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cosmetics_details')
    color = models.CharField(max_length=50, null=True, blank=True)
    skintype = models.CharField(max_length=50, null=True, blank=True)
    shades = models.IntegerField(null=True, blank=True)
    waterproof = models.BooleanField(null=True, blank=True)
    colors = models.IntegerField(null=True, blank=True)
    scent = models.CharField(max_length=50, null=True, blank=True)
    pack = models.IntegerField(null=True, blank=True)
    spf = models.IntegerField(null=True, blank=True)

class Furniture(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='furniture_details')
    seats = models.IntegerField(null=True, blank=True)
    mesh = models.BooleanField(null=True, blank=True)
    wood = models.CharField(max_length=50, null=True, blank=True)
    frame = models.CharField(max_length=50, null=True, blank=True)
    led = models.BooleanField(null=True, blank=True)
    tiers = models.IntegerField(null=True, blank=True)
    eames = models.BooleanField(null=True, blank=True)
    ceramic = models.BooleanField(null=True, blank=True)

class Kitchenware(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='kitchenware_details')
    capacity = models.CharField(max_length=50, null=True, blank=True)
    preseasoned = models.BooleanField(null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    power = models.CharField(max_length=50, null=True, blank=True)
    smart = models.BooleanField(null=True, blank=True)
    retro = models.BooleanField(null=True, blank=True)
    temp_control = models.BooleanField(null=True, blank=True)

class Book(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='book_details')
    genre = models.CharField(max_length=50, null=True, blank=True)
    selfhelp = models.BooleanField(null=True, blank=True)
    classic = models.BooleanField(null=True, blank=True)
    fantasy = models.BooleanField(null=True, blank=True)
    history = models.BooleanField(null=True, blank=True)
    distopian = models.BooleanField(null=True, blank=True)
    bio = models.BooleanField(null=True, blank=True)

class Sportswear(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='sportswear_details')
    tech = models.CharField(max_length=50, null=True, blank=True)
    feel = models.CharField(max_length=50, null=True, blank=True)
    dry = models.CharField(max_length=50, null=True, blank=True)
    waterproof = models.BooleanField(null=True, blank=True)
    capacity = models.CharField(max_length=50, null=True, blank=True)
    retro = models.BooleanField(null=True, blank=True)
    stretch = models.CharField(max_length=50, null=True, blank=True)
    impact = models.CharField(max_length=50, null=True, blank=True)

class Accessories(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='accessories_details')
    lenses = models.CharField(max_length=50, null=True, blank=True)
    rfid = models.BooleanField(null=True, blank=True)
    volume = models.CharField(max_length=50, null=True, blank=True)
    one_size = models.BooleanField(null=True, blank=True)
    material = models.CharField(max_length=50, null=True, blank=True)
    buckle = models.CharField(max_length=50, null=True, blank=True)
    purity = models.CharField(max_length=50, null=True, blank=True)
    portable = models.BooleanField(null=True, blank=True)

class PurchaseHistory(models.Model):
    user_id = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='pending') # pending, completed, cancelled
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'purchase_history'
