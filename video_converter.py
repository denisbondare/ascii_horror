import cv2
import numpy as np
from PIL import Image

ASCII_CHARS = ['█', '█', '█', '▓', '▓', '▓', '▓', '░', '░', '░', '░']
ASCII_CHARS = ['=', '=', '=', '+', '+', '+', '-', '-', '-', '⠀', '⠀']
INVERTED_ASCII_CHARS = ASCII_CHARS[::-1]



def resize_image(image, new_width=42):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    return image.convert('L')

def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([INVERTED_ASCII_CHARS[pixel//25] for pixel in pixels])
    return characters

def convert_frame_to_ascii(frame, width):
    image = Image.fromarray(frame)
    image = resize_image(image, width)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image)
    return ascii_str

def convert_video_to_ascii(video_path, output_path, width=42):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    ascii_frames = []
    
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        ascii_frame = convert_frame_to_ascii(frame, width)
        ascii_frames.append(ascii_frame)
    
    cap.release()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{fps}\n")
        f.write(f"{width}\n")
        f.write(f"{len(ascii_frames[0]) // width}\n")
        for frame in ascii_frames:
            f.write(frame + '\n')
    
    print(f"Converted video saved to {output_path}")

if __name__ == "__main__":
    input_video = "input_video.mp4"
    output_file = "output_ascii_video.txt"
    convert_video_to_ascii(input_video, output_file, width=42)