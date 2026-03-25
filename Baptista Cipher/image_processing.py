from PIL import Image

def load_image(image_path):
    image = Image.open(image_path)
    pixels = list(image.getdata())
    width, height = image.size

    if image.mode == 'RGB':
        data = [value for pixel in pixels for value in pixel]
    else:
        data = list(pixels)

    return data, width, height, image.mode

def save_image(data, width, height, mode, output_path):
    if mode == 'RGB':
        pixels = [tuple(data[i:i+3]) for i in range(0, len(data), 3)]
    else:
        pixels = data

    image = Image.new(mode, (width, height))
    image.putdata(pixels)
    image.save(output_path)