import os
import django
import sys

def seed_mobiles():
    from mob_service.models import Mobile
    mobiles = [
        {"name": "iPhone 15 Pro", "brand": "Apple", "price": 999, "stock": 50, "description": "Siêu phẩm Apple 2024 titan tự nhiên"},
        {"name": "Galaxy S24 Ultra", "brand": "Samsung", "price": 1199, "stock": 40, "description": "Bút S-Pen thông minh, AI xử lý ảnh cực đỉnh"},
        {"name": "Xiaomi 14 Pro", "brand": "Xiaomi", "price": 899, "stock": 100, "description": "Ống kính Leica cao cấp, sạc siêu nhanh"},
        {"name": "Pixel 8 Pro", "brand": "Google", "price": 899, "stock": 30, "description": "Trải nghiệm Android thuần khiết nhất"},
        {"name": "Oppo Find X7", "brand": "Oppo", "price": 750, "stock": 45, "description": "Camera chân dung nghệ thuật"},
        {"name": "Sony Xperia 1 V", "brand": "Sony", "price": 1050, "stock": 20, "description": "Màn hình 4K HDR cho trải nghiệm điện ảnh"},
        {"name": "Asus ROG Phone 8", "brand": "Asus", "price": 950, "stock": 15, "description": "Gaming phone mạnh nhất thế giới"},
        {"name": "Vivo X100 Pro", "brand": "Vivo", "price": 820, "stock": 35, "description": "Ống kính ZEISS chụp ảnh chuyên nghiệp"},
        {"name": "Realme GT5", "brand": "Realme", "price": 600, "stock": 60, "description": "Hiệu năng trên giá thành cực tốt"},
        {"name": "Nokia G42 5G", "brand": "Nokia", "price": 250, "stock": 120, "description": "Điện thoại bền bỉ, dễ dàng sửa chữa"},
    ]
    for m in mobiles:
        Mobile.objects.get_or_create(name=m['name'], brand=m['brand'], defaults=m)
    print("Seeded 10+ Mobiles.")

def seed_computers():
    from computer_service.models import Computer
    computers = [
        {"name": "MacBook Air M3", "brand": "Apple", "price": 1099, "stock": 25, "description": "Mỏng nhẹ, pin trâu cho dân văn phòng"},
        {"name": "Dell XPS 15", "brand": "Dell", "price": 1499, "stock": 15, "description": "Màn hình InfinityEdge 4K tuyệt đẹp"},
        {"name": "ThinkPad X1 Carbon Gen 11", "brand": "Lenovo", "price": 1299, "stock": 20, "description": "Bền bỉ, bàn phím gõ sướng nhất"},
        {"name": "ROG Zephyrus G14 2024", "brand": "ASUS", "price": 1699, "stock": 10, "description": "Laptop gaming gọn nhẹ, màn hình OLED"},
        {"name": "HP Spectre x360", "brand": "HP", "price": 1350, "stock": 18, "description": "Laptop xoay gập 360 độ sang trọng"},
        {"name": "Surface Laptop 5", "brand": "Microsoft", "price": 1100, "stock": 25, "description": "Thiết kế tối giản, đồng bộ Windows cực tốt"},
        {"name": "Acer Predator Helios Neo 16", "brand": "Acer", "price": 1250, "stock": 22, "description": "Laptop gaming tản nhiệt cực mát"},
        {"name": "MSI Stealth 14 Studio", "brand": "MSI", "price": 1450, "stock": 12, "description": "Workstation kết hợp Gaming chuyên nghiệp"},
        {"name": "LG Gram 17 2024", "brand": "LG", "price": 1550, "stock": 8, "description": "Màn hình 17 inch siêu to nhưng nhẹ dưới 1.4kg"},
        {"name": "Razer Blade 16", "brand": "Razer", "price": 2800, "stock": 5, "description": "Đẳng cấp laptop cho game thủ và creator"},
    ]
    for c in computers:
        Computer.objects.get_or_create(name=c['name'], brand=c['brand'], defaults=c)
    print("Seeded 10+ Computers.")

def seed_clothes():
    from clothes_service.models import Clothes
    clothes = [
        {"name": "Áo thun Cotton Uniqlo", "brand": "Uniqlo", "price": 19, "stock": 200, "description": "Chất liệu Supima mềm mịn, thoáng mát"},
        {"name": "Quần Jeans Slim Fit Levi's", "brand": "Levi's", "price": 59, "stock": 150, "description": "Phom dáng trẻ trung, bền màu"},
        {"name": "Áo khoác da Bomber", "brand": "Zara", "price": 129, "stock": 50, "description": "Phong cách biker nam tính"},
        {"name": "Giày chạy bộ Air Max", "brand": "Nike", "price": 89, "stock": 80, "description": "Đệm khí êm ái cho vận động viên"},
        {"name": "Váy hoa Vintage", "brand": "H&M", "price": 45, "stock": 90, "description": "Nhẹ nhàng cho những buổi dạo phố"},
        {"name": "Áo sơ mi Oxford", "brand": "Brooks Brothers", "price": 85, "stock": 40, "description": "Chuẩn mực đồ công sở cao cấp"},
        {"name": "Quần Jogger nỉ", "brand": "Adidas", "price": 55, "stock": 110, "description": "Thoải mái tập luyện hoặc mặc ở nhà"},
        {"name": "Áo len Cashmere", "brand": "Mango", "price": 95, "stock": 35, "description": "Giữ ấm tốt, chất liệu len cao cấp nhất"},
        {"name": "Chân váy Pleated", "brand": "Pull&Bear", "price": 39, "stock": 70, "description": "Xếp ly thanh lịch, dễ phối đồ"},
        {"name": "Mũ lưỡi trai NY", "brand": "New Era", "price": 25, "stock": 300, "description": "Phụ kiện thời trang đường phố classic"},
    ]
    for c in clothes:
        Clothes.objects.get_or_create(name=c['name'], brand=c['brand'], defaults=c)
    print("Seeded 10+ Clothes.")

if __name__ == "__main__":
    service = sys.argv[1] if len(sys.argv) > 1 else None
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Add project root to sys.path
    sys.path.append('/app')
    
    if service == 'mob':
        sys.path.append('/app/mob_service')
        django.setup()
        seed_mobiles()
    elif service == 'computer':
        sys.path.append('/app/computer_service')
        django.setup()
        seed_computers()
    elif service == 'clothes':
        sys.path.append('/app/clothes_service')
        django.setup()
        seed_clothes()
    else:
        print("Usage: python seed.py [mob|computer|clothes]")
