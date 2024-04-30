import os
from PIL import Image
import matplotlib.pyplot as plt

class ImageSchema:
    def __init__(self, images_folder):
        self.images_folder = images_folder

    def dataset_analysis(self):
        """
        This method displays images from the specified folder.
        """
        fig = plt.figure(figsize=(30, 30))
        rows = 1
        columns = 10
        for idx, filename in enumerate(os.listdir(self.images_folder)):
            image_path = os.path.join(self.images_folder, filename)
            if os.path.isfile(image_path):  # Check if the path points to a file
                try:
                    image = Image.open(image_path)
                    fig.add_subplot(rows, columns, idx+1)
                    plt.imshow(image)
                    plt.axis("off")
                    plt.title(filename)  # Use filename as title
                except Exception as e:
                    print(f"Unable to load image: {filename}, Error: {e}")
            else:
                print(f"Not a file: {image_path}")

        plt.show()  # Display the images

# Utilizzo della classe ImageSchema
image_schema = ImageSchema("/app/cat/data/coachcat/image")
image_schema.dataset_analysis()
