from bing_image_downloader import downloader

# 1. Set specific Windows folder path
custom_folder = r"C:\Users\vasam\OneDrive\Desktop\attendance\testing"

# 2. List 30 Indian players
players = [
    "Rohit Sharma", "Yashasvi Jaiswal", "Shubman Gill", "Ruturaj Gaikwad", "Sai Sudharsan",
    "Virat Kohli", "Suryakumar Yadav", "Shreyas Iyer", "Rinku Singh", "Sarfaraz Khan",
    "Rajat Patidar", "Devdutt Padikkal", "Rishabh Pant", "KL Rahul", "Sanju Samson",
    "Ishan Kishan", "Dhruv Jurel", "Hardik Pandya", "Ravindra Jadeja", "Axar Patel",
    "Washington Sundar", "Shivam Dube", "Ravichandran Ashwin", "Kuldeep Yadav", "Ravi Bishnoi",
    "Yuzvendra Chahal", "Jasprit Bumrah", "Mohammed Siraj", "Mohammed Shami", "Arshdeep Singh"
]

# 3. Loop through players
for player in players:
    
    # 4. Download 2 images per player
    downloader.download(
        player, 
        limit=5, 
        output_dir=custom_folder, 
        adult_filter_off=True, 
        force_replace=False, 
        timeout=60, 
        verbose=False
    )
