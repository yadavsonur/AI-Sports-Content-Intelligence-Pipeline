from PIL import Image

for path in [
    "assets/image1.jpg",
    "assets/image2.jpg",
    "assets/image3.jpg"
]:
    img = Image.open(path)
    print(path, img.size)