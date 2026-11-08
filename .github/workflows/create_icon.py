from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon():
    # Create a 256x256 high-contrast image (Black background, bright yellow/white graphics)
    size = (256, 256)
    image = Image.new("RGBA", size, (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)

    # Draw high-contrast outer border
    draw.rectangle([10, 10, 246, 246], outline=(255, 255, 0), width=8)

    # Draw a stylized paintbrush and sound waves
    # Paintbrush handle
    draw.polygon([(180, 40), (210, 70), (140, 140), (110, 110)], fill=(255, 255, 255))
    # Brush tip
    draw.polygon([(110, 110), (140, 140), (90, 150)], fill=(255, 255, 0))

    # Sound waves representing audio feedback
    draw.arc([40, 60, 120, 140], start=270, end=90, fill=(0, 255, 255), width=6)
    draw.arc([20, 40, 140, 160], start=270, end=90, fill=(0, 255, 255), width=6)

    # Save as icon.ico with multiple resolutions
    os.makedirs(".", exist_ok=True)
    image.save("icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("High-contrast icon.ico generated successfully.")

if __name__ == "__main__":
    generate_icon()
