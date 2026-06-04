import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.config.settings')
django.setup()

from product_service.models import Product, PurchaseHistory

def seed_behavioral_data():
    print("🌱 Seeding Behavioral Purchase History...")
    
    # 1. Clear existing history to avoid duplicates
    PurchaseHistory.objects.all().delete()
    
    # 2. Get categorized products
    all_prods = list(Product.objects.all())
    tech_prods = [p for p in all_prods if p.category_name in ['Mobile', 'Computer', 'Watches']]
    fashion_prods = [p for p in all_prods if p.category_name in ['Clothes', 'Shoes', 'Jewelry', 'Cosmetics']]
    kitchen_prods = [p for p in all_prods if p.category_name in ['Kitchenware']]
    
    # Define User Patterns
    # User 1: The Techie
    for _ in range(8):
        PurchaseHistory.objects.create(user_id=1, product=random.choice(tech_prods), quantity=1, status='completed')
    
    # User 2: The Fashionista
    for _ in range(12):
        PurchaseHistory.objects.create(user_id=2, product=random.choice(fashion_prods), quantity=1, status='completed')
    
    # User 3: The Chef
    for _ in range(6):
        PurchaseHistory.objects.create(user_id=3, product=random.choice(kitchen_prods), quantity=1, status='completed')
        
    # User 4: Mixed (Similar to User 1)
    for _ in range(3):
        PurchaseHistory.objects.create(user_id=4, product=random.choice(tech_prods), quantity=1, status='completed')
    
    print(f"✅ Created {PurchaseHistory.objects.count()} purchase records for behavioral analysis!")

if __name__ == "__main__":
    seed_behavioral_data()
