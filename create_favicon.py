from PIL import Image

favicon = Image.new('RGB', (32, 32), color='#7FFF00')
favicon.save('static/images/icon.ico', format='ICO')
print("Created icon.ico (32x32)")
