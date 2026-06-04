import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_user_behavior_data(num_users=500, events_per_user=8):
    # Categories and Sample Products based on seed.py
    categories = {
        'Mobile': ['iPhone 15 Pro', 'Galaxy S24 Ultra', 'Pixel 8 Pro', 'OnePlus 12', 'Xperia 1 V', 'Redmi Note 13', 'Nothing Phone 2', 'Z Flip 5'],
        'Computer': ['MacBook Air M3', 'ROG Zephyrus G14', 'XPS 13', 'ThinkPad X1 Carbon', 'Surface Laptop 5', 'Razer Blade 15', 'Pavilion 15', 'Vivobook S'],
        'Clothes': ['Classic White Tee', 'Slim Fit Jeans', 'Denim Jacket', 'Oxford Shirt', 'Cargo Pants', 'Hoodie', 'Silk Scarf', 'Winter Parka'],
        'Shoes': ['Air Max 270', 'Ultraboost 22', 'Old Skool', 'Chuck 70', 'Clyde All-Pro', 'Classic Leather', 'Cloud 5', '990v6'],
        'Watches': ['Submariner', 'G-Shock DW5600', 'Seamaster', 'Apple Watch S9', 'Tissot Le Locle', 'Seiko 5 Sport', 'Tank Must', 'F91W'],
        'Cosmetics': ['Matte Lipstick', 'Hydrating Serum', 'Foundation Pro', 'Long Lash Mascara', 'Naked Palette', 'Perfume No.5', 'Sheet Mask', 'Sunscreen 50+'],
        'Furniture': ['Modern Sofa', 'ErgoChair', 'Coffee Table', 'Queen Bed', 'Desk Lamp', 'Bookshelf', 'Dining Chair', 'Vase'],
        'Kitchenware': ['Air Fryer', 'Cast Iron Skillet', 'Stand Mixer', 'Chef\'s Knife', 'Blender', 'Pressure Cooker', 'Toaster', 'Kettle'],
        'Books': ['Clean Code', 'Dune', 'Atomic Habits', 'The Great Gatsby', 'Harry Potter 1', 'Sapiens', '1984', 'Steve Jobs'],
        'Sportswear': ['Dri-FIT Tee', 'Yoga Pants', 'Running Shorts', 'Windbreaker', 'Gym Bag', 'Tracksuit', 'Compression Tights', 'Sports Bra'],
        'Accessories': ['Wayfarer', 'Leather Wallet', 'Tech Backpack', 'Cotton Beanie', 'Silk Tie', 'Leather Belt', 'Silver Ring', 'Capsule Umberella']
    }

    actions = ['view', 'click', 'add_to_cart', 'purchase']
    # Probabilities for actions: view is most common, purchase is least
    action_probs = [0.5, 0.3, 0.15, 0.05]

    data = []
    start_time = datetime.now() - timedelta(days=30)

    for user_id in range(1, num_users + 1):
        # Each user has a "favorite" category they interact with more
        fav_cat = random.choice(list(categories.keys()))
        
        for _ in range(events_per_user):
            # 70% chance to pick from favorite category, 30% from others
            if random.random() < 0.7:
                cat = fav_cat
            else:
                cat = random.choice(list(categories.keys()))
            
            product = random.choice(categories[cat])
            action = np.random.choice(actions, p=action_probs)
            
            # Random time in the last 30 days
            timestamp = start_time + timedelta(
                seconds=random.randint(0, 30 * 24 * 3600)
            )
            
            data.append({
                'user_id': user_id,
                'product_id': product,  # In this simplified case, we use product name as ID
                'category': cat,
                'action': action,
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    df = pd.DataFrame(data)
    # Sort by timestamp to make sequences logical
    df = df.sort_values('timestamp')
    
    os.makedirs('data', exist_ok=True)
    output_path = 'data/data_user500.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} events for {num_users} users.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    generate_user_behavior_data()
