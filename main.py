import struct
import array
from PIL import Image
import os

def read_uint32(file):
    return struct.unpack('<I', file.read(4))[0]

def write_uint32(file, value):
    file.write(struct.pack('<I', value))

def convert_to_bmp(input_file, output_file):
    with open(input_file, 'rb') as f:
        # Read header
        magic_code = read_uint32(f)
        if magic_code != 0x4D544942:  # "BITM" in little endian
            raise ValueError(f"Invalid magic code in {input_file}")
        
        width = read_uint32(f)
        height = read_uint32(f)
        
        # Read image data
        data = array.array('I')
        data.fromfile(f, (width * height + 31) // 32)
        
        # Create a new image
        img = Image.new('1', (width, height))
        pixels = img.load()
        
        # Fill the image with pixel data
        for y in range(height):
            for x in range(width):
                word_index = (y * width + x) // 32
                bit_index = (y * width + x) % 32
                pixel = (data[word_index] >> bit_index) & 1
                pixels[x, y] = 255 if pixel == 0 else 0  # 255 (white) for 0, 0 (black) for 1
        
        # Save as BMP
        img.save(output_file, 'BMP')

def convert_to_custom(input_file, output_file):
    # Open the BMP file
    img = Image.open(input_file)
    
    # Ensure the image is in black and white mode
    img = img.convert('1')
    
    width, height = img.size
    pixels = img.load()
    
    # Calculate the number of 32-bit words needed
    word_count = (width * height + 31) // 32
    
    # Create an array to hold the bitmap data
    data = array.array('I', [0] * word_count)
    
    # Convert pixel data
    for y in range(height):
        for x in range(width):
            word_index = (y * width + x) // 32
            bit_index = (y * width + x) % 32
            if pixels[x, y] == 0:  # Black pixel
                data[word_index] |= (1 << bit_index)
    
    # Write to custom format file
    with open(output_file, 'wb') as f:
        # Write header
        write_uint32(f, 0x4D544942)  # Magic code "BITM"
        write_uint32(f, width)
        write_uint32(f, height)
        
        # Write bitmap data
        data.tofile(f)

# Batch conversion for BMP to custom format
def batch_bmp_to_custom(bmp_files, output_folder):
    for bmp_file in bmp_files:
        bmp_filename = os.path.basename(bmp_file)
        output_file = os.path.join(output_folder, os.path.splitext(bmp_filename)[0] + '.bin')
        convert_to_custom(bmp_file, output_file)
        print(f"Conversion complete for {bmp_file}. Output saved as {output_file}")

# Batch conversion for custom format to BMP
def batch_custom_to_bmp(custom_files, output_folder):
    for custom_file in custom_files:
        custom_filename = os.path.basename(custom_file)
        output_file = os.path.join(output_folder, os.path.splitext(custom_filename)[0] + '_converted.bmp')
        convert_to_bmp(custom_file, output_file)
        print(f"Conversion complete for {custom_file}. Output saved as {output_file}")

# Usage examples
bmp_files = ['1.bmp', '2.bmp']
custom_files = ['1.bin', '2.bin']

# Example paths, change the output folder paths as needed
output_folder_custom = ''
output_folder_bmp = ''

# Uncomment one of the lines below to use batch processing
# batch_bmp_to_custom(bmp_files, output_folder_custom)
# batch_custom_to_bmp(custom_files, output_folder_bmp)
