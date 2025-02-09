import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the pre-trained model
model = load_model('D:\hack\model.h5')

def predict_fire(image_path):
    """
    Predict whether the image contains fire or not.

    Parameters:
    image_path (str): The path to the input image.

    Returns:
    str: 'Fire' if fire is detected, 'No Fire' otherwise.
    """
    # Load and preprocess the image
    img = cv2.imread(image_path)
    image = cv2.resize(img,(32,32))
    image = np.array(image)
    image = image/255
    img = np.array([image])
    # Make a prediction
    prediction = model.predict(img)

    # Determine the result
    result = 'Fire' if prediction[0][0] > 0.5 else 'No Fire'

    return result

image_path = r"D:\hack\valid\wildfire\-57.3633,51.4978.jpg"
print(predict_fire(image_path))
