import cv2
import numpy as np

# --- SETTINGS ---
# Replace this with the actual path to one of your images
image_path =  r"C:\Users\parastoo\PycharmProjects\PythonProject\Images_dataset\Images_dataset\S4SAVF03-20220906-15W.png"

# main_first. Load the Image
img = cv2.imread(image_path)

if img is None:
    print(f"❌ Error: Could not find image at {image_path}")
    print("Make sure the image file is in the same folder as this script!")
else:
    # 2. Convert BGR (OpenCV default) to RGB (What your project uses)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 3. Define the Rust Color Range (EXACTLY matching your process_images.py)
    # Your code uses: lower=[50,0,0], upper=[255,100,80]
    lower_rust = np.array([50, 0, 0])
    upper_rust = np.array([255, 100, 80])

    # 4. Create the Mask
    # This finds pixels that fall inside that red/brown range
    mask = cv2.inRange(img_rgb, lower_rust, upper_rust)

    # 5. Save the result
    cv2.imwrite("Slide_Presentation_Mask.png", mask)
    print("✅ Success! 'Slide_Presentation_Mask.png' has been saved.")
    print("You can now insert this black-and-white image into your PowerPoint.")