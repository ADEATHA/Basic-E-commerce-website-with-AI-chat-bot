import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from product_service.models import Product, Category
from product_service import models as product_models

def seed_products():
    Product.objects.all().delete()
    Category.objects.all().delete()

    categories_data = {
        'Mobile': [
            {"name": "iPhone 15 Pro", "brand": "Apple", "price": "1000", "img": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&q=80&w=400", "attrs": {"storage": "256GB"}},
            {"name": "Galaxy S24 Ultra", "brand": "Samsung", "price": "1200", "img": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&q=80&w=400", "attrs": {"storage": "512GB"}},
            {"name": "Pixel 8 Pro", "brand": "Google", "price": "899", "img": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&q=80&w=400", "attrs": {"camera": "50MP"}},
            {"name": "OnePlus 12", "brand": "OnePlus", "price": "799", "img": "https://images.unsplash.com/photo-1510557880182-3d4d3cba3f9e?auto=format&fit=crop&q=80&w=400", "attrs": {"ram": "16GB"}},
            {"name": "Xperia 1 V", "brand": "Sony", "price": "1199", "img": "https://images.unsplash.com/photo-1544244015-0cd4b3ffeb8e?auto=format&fit=crop&q=80&w=400", "attrs": {"display": "4K OLED"}},
            {"name": "Redmi Note 13", "brand": "Xiaomi", "price": "299", "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&q=80&w=400", "attrs": {"battery": "5000mAh"}},
            {"name": "Nothing Phone 2", "brand": "Nothing", "price": "599", "img": "https://images.unsplash.com/photo-1556656793-062ff9878258?auto=format&fit=crop&q=80&w=400", "attrs": {"design": "Glyph Interface"}},
            {"name": "Z Flip 5", "brand": "Samsung", "price": "999", "img": "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?auto=format&fit=crop&q=80&w=400", "attrs": {"type": "Foldable"}}
        ],
        'Computer': [
            {"name": "MacBook Air M3", "brand": "Apple", "price": "1099", "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&q=80&w=400", "attrs": {"cpu": "M3"}},
            {"name": "ROG Zephyrus G14", "brand": "ASUS", "price": "1599", "img": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&q=80&w=400", "attrs": {"gpu": "RTX 4070"}},
            {"name": "XPS 13", "brand": "Dell", "price": "999", "img": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&q=80&w=400", "attrs": {"weight": "1.2kg"}},
            {"name": "ThinkPad X1 Carbon", "brand": "Lenovo", "price": "1299", "img": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&q=80&w=400", "attrs": {"durability": "Military Grade"}},
            {"name": "Surface Laptop 5", "brand": "Microsoft", "price": "899", "img": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&q=80&w=400", "attrs": {"screen": "Touchscreen"}},
            {"name": "Razer Blade 15", "brand": "Razer", "price": "2499", "img": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&q=80&w=400", "attrs": {"refresh_rate": "240Hz"}},
            {"name": "Pavilion 15", "brand": "HP", "price": "649", "img": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&q=80&w=400", "attrs": {"ram": "8GB"}},
            {"name": "Vivobook S", "brand": "ASUS", "price": "749", "img": "https://images.unsplash.com/photo-1611186871348-b1fc6f1432f4?auto=format&fit=crop&q=80&w=400", "attrs": {"color": "Blue"}}
        ],
        'Clothes': [
            {"name": "Classic White Tee", "brand": "Uniqlo", "price": "19", "img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&q=80&w=400", "attrs": {"material": "Cotton"}},
            {"name": "Slim Fit Jeans", "brand": "Levi's", "price": "59", "img": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&q=80&w=400", "attrs": {"fit": "Slim"}},
            {"name": "Denim Jacket", "brand": "Zara", "price": "79", "img": "https://images.unsplash.com/photo-1576905341939-424af1956570?auto=format&fit=crop&q=80&w=400", "attrs": {"style": "Biker"}},
            {"name": "Oxford Shirt", "brand": "Ralph Lauren", "price": "95", "img": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&q=80&w=400", "attrs": {"pattern": "Striped"}},
            {"name": "Cargo Pants", "brand": "H&M", "price": "34", "img": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&q=80&w=400", "attrs": {"pockets": 6}},
            {"name": "Hoodie", "brand": "Champion", "price": "45", "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&q=80&w=400", "attrs": {"fabric": "Heavy"}},
            {"name": "Silk Scarf", "brand": "Hermes", "price": "450", "img": "https://images.unsplash.com/photo-1558021211-1da4b7f73977?auto=format&fit=crop&q=80&w=400", "attrs": {"luxury": True}},
            {"name": "Winter Parka", "brand": "Canada Goose", "price": "1200", "img": "https://images.unsplash.com/photo-1539533213203-217768528f8d?auto=format&fit=crop&q=80&w=400", "attrs": {"temp": "-30C"}}
        ],
        'Shoes': [
            {"name": "Air Max 270", "brand": "Nike", "price": "150", "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=400", "attrs": {"cushion": "Air"}},
            {"name": "Ultraboost 22", "brand": "Adidas", "price": "180", "img": "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?auto=format&fit=crop&q=80&w=400", "attrs": {"tech": "Boost"}},
            {"name": "Old Skool", "brand": "Vans", "price": "65", "img": "https://images.unsplash.com/photo-1525966222134-fcfa99bcfde2?auto=format&fit=crop&q=80&w=400", "attrs": {"style": "Skate"}},
            {"name": "Chuck 70", "brand": "Converse", "price": "85", "img": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&q=80&w=400", "attrs": {"material": "Canvas"}},
            {"name": "Clyde All-Pro", "brand": "Puma", "price": "120", "img": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&q=80&w=400", "attrs": {"type": "Basketball"}},
            {"name": "Classic Leather", "brand": "Reebok", "price": "75", "img": "https://images.unsplash.com/photo-1512374382149-233c42b6a83b?auto=format&fit=crop&q=80&w=400", "attrs": {"retro": True}},
            {"name": "Cloud 5", "brand": "On", "price": "140", "img": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&q=80&w=400", "attrs": {"weight": "Light"}},
            {"name": "990v6", "brand": "New Balance", "price": "200", "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&q=80&w=400", "attrs": {"support": "High"}}
        ],
        'Watches': [
            {"name": "Submariner", "brand": "Rolex", "price": "8500", "img": "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&q=80&w=400", "attrs": {"water": "300m"}},
            {"name": "G-Shock DW5600", "brand": "Casio", "price": "75", "img": "https://images.unsplash.com/photo-1508057198894-247b23fe5ade?auto=format&fit=crop&q=80&w=400", "attrs": {"shock": "High"}},
            {"name": "Seamaster", "brand": "Omega", "price": "5200", "img": "https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?auto=format&fit=crop&q=80&w=400", "attrs": {"movement": "Co-Axial"}},
            {"name": "Apple Watch S9", "brand": "Apple", "price": "399", "img": "https://images.unsplash.com/photo-1544117518-306364ac3030?auto=format&fit=crop&q=80&w=400", "attrs": {"os": "watchOS"}},
            {"name": "Tissot Le Locle", "brand": "Tissot", "price": "550", "img": "https://images.unsplash.com/photo-1612817159949-195b6eb9e31a?auto=format&fit=crop&q=80&w=400", "attrs": {"style": "Dress"}},
            {"name": "Seiko 5 Sport", "brand": "Seiko", "price": "285", "img": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?auto=format&fit=crop&q=80&w=400", "attrs": {"lume": "Strong"}},
            {"name": "Tank Must", "brand": "Cartier", "price": "3400", "img": "https://images.unsplash.com/photo-1509112756314-34a065551980?auto=format&fit=crop&q=80&w=400", "attrs": {"iconic": True}},
            {"name": "F91W", "brand": "Casio", "price": "18", "img": "https://images.unsplash.com/photo-1622434641406-a158123450f9?auto=format&fit=crop&q=80&w=400", "attrs": {"classic": True}}
        ],
        'Cosmetics': [
            {"name": "Matte Lipstick", "brand": "MAC", "price": "25", "img": "https://images.unsplash.com/photo-1586776977607-310e9c725c37?auto=format&fit=crop&q=80&w=400", "attrs": {"color": "Red"}},
            {"name": "Hydrating Serum", "brand": "Estee Lauder", "price": "105", "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&q=80&w=400", "attrs": {"skintype": "Dry"}},
            {"name": "Foundation Pro", "brand": "Fenty", "price": "38", "img": "https://images.unsplash.com/photo-1596462502278-27bfdc4033c8?auto=format&fit=crop&q=80&w=400", "attrs": {"shades": 50}},
            {"name": "Long Lash Mascara", "brand": "Lancôme", "price": "32", "img": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&q=80&w=400", "attrs": {"waterproof": True}},
            {"name": "Naked Palette", "brand": "Urban Decay", "price": "54", "img": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&q=80&w=400", "attrs": {"colors": 12}},
            {"name": "Perfume No.5", "brand": "Chanel", "price": "160", "img": "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&q=80&w=400", "attrs": {"scent": "Floral"}},
            {"name": "Sheet Mask", "brand": "Skinfood", "price": "3", "img": "https://images.unsplash.com/photo-1601049541289-9b1b7abcad59?auto=format&fit=crop&q=80&w=400", "attrs": {"pack": 10}},
            {"name": "Sunscreen 50+", "brand": "La Roche", "price": "28", "img": "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?auto=format&fit=crop&q=80&w=400", "attrs": {"spf": 50}}
        ],
        'Furniture': [
            {"name": "Modern Sofa", "brand": "IKEA", "price": "499", "img": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=400", "attrs": {"seats": 3}},
            {"name": "ErgoChair", "brand": "Autonomous", "price": "549", "img": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?auto=format&fit=crop&q=80&w=400", "attrs": {"mesh": True}},
            {"name": "Coffee Table", "brand": "West Elm", "price": "299", "img": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?auto=format&fit=crop&q=80&w=400", "attrs": {"wood": "Oak"}},
            {"name": "Queen Bed", "brand": "Zinus", "price": "350", "img": "https://images.unsplash.com/photo-1505693419148-ad3b471e4fd5?auto=format&fit=crop&q=80&w=400", "attrs": {"frame": "Metal"}},
            {"name": "Desk Lamp", "brand": "Philips", "price": "45", "img": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=400", "attrs": {"led": True}},
            {"name": "Bookshelf", "brand": "Target", "price": "89", "img": "https://images.unsplash.com/photo-1594620302200-9a762244a156?auto=format&fit=crop&q=80&w=400", "attrs": {"tiers": 5}},
            {"name": "Dining Chair", "brand": "Herman Miller", "price": "800", "img": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?auto=format&fit=crop&q=80&w=400", "attrs": {"eames": True}},
            {"name": "Vase", "brand": "HomeDecor", "price": "25", "img": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?auto=format&fit=crop&q=80&w=400", "attrs": {"ceramic": True}}
        ],
        'Kitchenware': [
            {"name": "Air Fryer", "brand": "Ninja", "price": "149", "img": "https://images.unsplash.com/photo-1584286595398-a59f21d313f5?auto=format&fit=crop&q=80&w=400", "attrs": {"capacity": "5L"}},
            {"name": "Cast Iron Skillet", "brand": "Lodge", "price": "35", "img": "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?auto=format&fit=crop&q=80&w=400", "attrs": {"preseasoned": True}},
            {"name": "Stand Mixer", "brand": "KitchenAid", "price": "399", "img": "https://images.unsplash.com/photo-1594385208974-2e75f9d8ad48?auto=format&fit=crop&q=80&w=400", "attrs": {"speed": 10}},
            {"name": "Chef's Knife", "brand": "Wüsthof", "price": "170", "img": "https://images.unsplash.com/photo-1593618998160-e34014e67546?auto=format&fit=crop&q=80&w=400", "attrs": {"length": "8 inch"}},
            {"name": "Blender", "brand": "Vitamix", "price": "499", "img": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?auto=format&fit=crop&q=80&w=400", "attrs": {"power": "2HP"}},
            {"name": "Pressure Cooker", "brand": "Instant Pot", "price": "99", "img": "https://images.unsplash.com/photo-1584985614482-17f032ff52d0?auto=format&fit=crop&q=80&w=400", "attrs": {"smart": True}},
            {"name": "Toaster", "brand": "Smeg", "price": "199", "img": "https://images.unsplash.com/photo-1583225026903-88ec0bc23b37?auto=format&fit=crop&q=80&w=400", "attrs": {"retro": True}},
            {"name": "Kettle", "brand": "Fellow", "price": "165", "img": "https://images.unsplash.com/photo-1594041157843-c0383785434d?auto=format&fit=crop&q=80&w=400", "attrs": {"temp_control": True}}
        ],
        'Books': [
            {"name": "Clean Code", "brand": "Uncle Bob", "price": "45", "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&q=80&w=400", "attrs": {"genre": "CS"}},
            {"name": "Dune", "brand": "Frank Herbert", "price": "18", "img": "https://images.unsplash.com/photo-1618335829737-2228adfb8b82?auto=format&fit=crop&q=80&w=400", "attrs": {"genre": "SciFi"}},
            {"name": "Atomic Habits", "brand": "James Clear", "price": "22", "img": "https://images.unsplash.com/photo-1589998059171-988d887df646?auto=format&fit=crop&q=80&w=400", "attrs": {"selfhelp": True}},
            {"name": "The Great Gatsby", "brand": "Fitzgerald", "price": "15", "img": "https://images.unsplash.com/photo-1543004629-ff569f872783?auto=format&fit=crop&q=80&w=400", "attrs": {"classic": True}},
            {"name": "Harry Potter 1", "brand": "JK Rowling", "price": "25", "img": "https://images.unsplash.com/photo-1626618012641-bfbca5a31239?auto=format&fit=crop&q=80&w=400", "attrs": {"fantasy": True}},
            {"name": "Sapiens", "brand": "Harari", "price": "28", "img": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=400", "attrs": {"history": True}},
            {"name": "1984", "brand": "George Orwell", "price": "12", "img": "https://images.unsplash.com/photo-1614543549304-9b244aa68c2c?auto=format&fit=crop&q=80&w=400", "attrs": {"distopian": True}},
            {"name": "Steve Jobs", "brand": "Isaacson", "price": "30", "img": "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&q=80&w=400", "attrs": {"bio": True}}
        ],
        'Sportswear': [
            {"name": "Dri-FIT Tee", "brand": "Nike", "price": "35", "img": "https://images.unsplash.com/photo-1571945153237-4929e783ee4a?auto=format&fit=crop&q=80&w=400", "attrs": {"tech": "DriFIT"}},
            {"name": "Yoga Pants", "brand": "Lululemon", "price": "118", "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=400", "attrs": {"feel": "Nulu"}},
            {"name": "Running Shorts", "brand": "Under Armour", "price": "28", "img": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&q=80&w=400", "attrs": {"dry": "Quick"}},
            {"name": "Windbreaker", "brand": "The North Face", "price": "99", "img": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&q=80&w=400", "attrs": {"waterproof": True}},
            {"name": "Gym Bag", "brand": "Adidas", "price": "45", "img": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&q=80&w=400", "attrs": {"capacity": "40L"}},
            {"name": "Tracksuit", "brand": "Puma", "price": "85", "img": "https://images.unsplash.com/photo-1483726234545-481d6e880fc6?auto=format&fit=crop&q=80&w=400", "attrs": {"retro": True}},
            {"name": "Compression Tights", "brand": "Gymshark", "price": "40", "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&q=80&w=400", "attrs": {"stretch": "4way"}},
            {"name": "Sports Bra", "brand": "Reebok", "price": "30", "img": "https://images.unsplash.com/photo-1518310383802-640c2de311b2?auto=format&fit=crop&q=80&w=400", "attrs": {"impact": "High"}}
        ],
        'Accessories': [
            {"name": "Wayfarer", "brand": "Ray-Ban", "price": "160", "img": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&q=80&w=400", "attrs": {"lenses": "Polarized"}},
            {"name": "Leather Wallet", "brand": "Bellroy", "price": "89", "img": "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&q=80&w=400", "attrs": {"rfid": True}},
            {"name": "Tech Backpack", "brand": "Peak Design", "price": "299", "img": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&q=80&w=400", "attrs": {"volume": "30L"}},
            {"name": "Cotton Beanie", "brand": "Carhartt", "price": "25", "img": "https://images.unsplash.com/photo-1576871337622-98d48d890e49?auto=format&fit=crop&q=80&w=400", "attrs": {"one_size": True}},
            {"name": "Silk Tie", "brand": "Brooks Brothers", "price": "85", "img": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&q=80&w=400", "attrs": {"material": "Silk"}},
            {"name": "Leather Belt", "brand": "Gucci", "price": "450", "img": "https://images.unsplash.com/photo-1624222247344-550fb805831f?auto=format&fit=crop&q=80&w=400", "attrs": {"buckle": "Double G"}},
            {"name": "Silver Ring", "brand": "Tiffany", "price": "300", "img": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&q=80&w=400", "attrs": {"purity": "925"}},
            {"name": "Capsule Umberella", "brand": "Dulton", "price": "35", "img": "https://images.unsplash.com/photo-1588615419957-bc66d953683a?auto=format&fit=crop&q=80&w=400", "attrs": {"portable": True}}
        ]
    }

    mapping = {
        'mobile': product_models.Mobile, 'computer': product_models.Computer, 
        'clothes': product_models.Clothes, 'shoes': product_models.Shoes, 
        'watches': product_models.Watches, 'cosmetics': product_models.Cosmetics,
        'furniture': product_models.Furniture, 'kitchenware': product_models.Kitchenware, 
        'books': product_models.Book, 'book': product_models.Book, 
        'sportswear': product_models.Sportswear, 'accessories': product_models.Accessories
    }

    count = 0
    for cat_name, items in categories_data.items():
        category, _ = Category.objects.get_or_create(name=cat_name)
        for item in items:
            p = Product.objects.create(
                name=item['name'],
                brand=item['brand'],
                category=category,
                price=item['price'],
                stock=random.randint(10, 100),
                image_url=item['img'],
                description=f"Sản phẩm {item['name']} cao cấp đến từ thương hiệu {item['brand']}. Phù hợp với nhu cầu hiện đại."
            )
            
            attrs = item.get('attrs', {})
            model_class = mapping.get(cat_name.lower())
            if model_class:
                valid_fields = [f.name for f in model_class._meta.fields if f.name not in ['id', 'product']]
                model_attrs = {k: v for k, v in attrs.items() if k in valid_fields}
                model_class.objects.create(product=p, **model_attrs)
            count += 1
            
    print(f"✅ Đã cập nhật {count} sản phẩm đa dạng trên {len(categories_data)} danh mục thành công!")

if __name__ == "__main__":
    seed_products()
