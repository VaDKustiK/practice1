from PIL import Image, ImageDraw

picture = Image.new('RGB', (300, 200), color='#E8E8E8')
draw = ImageDraw.Draw(picture)

draw.rectangle([100, 50, 200, 150], outline='#999999', width=3)
draw.text((150, 170), 'No Image', fill='#666666', anchor='mm')

picture.save('static/images/picture.png')
print("Created picture.png (300x200)")

logo = Image.new('RGB', (400, 100), color='#7FFF00')
draw_logo = ImageDraw.Draw(logo)

draw_logo.text((200, 50), 'ООО «Обувь»', fill='#000000', anchor='mm',
               font=None)

logo.save('static/images/logo.png')
print("Created logo.png (400x100)")

print("\nPlaceholder images created successfully!")
print("Note: These are simple placeholders. Replace with actual images.")
