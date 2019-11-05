from keras.models import load_model
from helpers import resize_to_fit
from imutils import paths
import numpy as np
import imutils
import cv2
import pickle
from PIL import Image, ImageEnhance, ImageFilter

def solve_captchas_with_model():

    MODEL_FILENAME = "captcha_model.hdf5"
    MODEL_LABELS_FILENAME = "model_labels.dat"
    CAPTCHA_IMAGE_FOLDER = "generated_captcha_images_test"
    PATH_IMAGE_CAPTCHA = "image_captcha.png"

    # Load up the model labels (so we can translate model predictions to actual letters)
    with open(MODEL_LABELS_FILENAME, "rb") as f:
        lb = pickle.load(f)

    # Load the trained neural network
    model = load_model(MODEL_FILENAME)

    image = cv2.imread(PATH_IMAGE_CAPTCHA)
        
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Add some extra padding around the image
    #image = cv2.copyMakeBorder(image, 20, 20, 20, 20, cv2.BORDER_REPLICATE)

    #threshold the image (convert it to pure black and white)
    #thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    retval, img_edge = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)
    img_blur = cv2.medianBlur(img_edge, 5)
    img = img_blur
        # Sort the detected letter images based on the x coordinate to make sure
        # we are processing them from left-to-right so we match the right image
        # with the right letter
    #letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])
        # Create an output image and a list to hold our predicted letters
    output = cv2.merge([img] * 3)
    predictions = []

    #img = image
    height, width = img.shape

    right = int (width/6)
    size_separator = 24
    
    for i in range(4):
        left =  right
        top = 1
        right = int(width/6) + size_separator
        bottom = height
        size_separator = size_separator + 18
            
        letter_image = img[top:bottom, left:right]
        
        letter_image = resize_to_fit(letter_image, 32, 116)
        #cv2.imshow("img",letter_image)
        #cv2.waitKey(0)

        # Turn the single image into a 4d list of images to make Keras happy
        letter_image = np.expand_dims(letter_image, axis=2)
        letter_image = np.expand_dims(letter_image, axis=0)
        
        # Ask the neural network to make a prediction
        prediction = model.predict(letter_image)

        # Convert the one-hot-encoded prediction back to a normal letter
        letter = lb.inverse_transform(prediction)[0]
        predictions.append(letter)

            # draw the prediction on the output image
        #cv2.rectangle(output, (x - 2, y - 2), (x + w + 4, y + h + 4), (0, 255, 0), 1)
        #cv2.putText(output, letter, (x - 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    # Print the captcha's text
    captcha_text = "".join(predictions)
    #print("CAPTCHA text is: {}".format(captcha_text))
    #else:
     #   captcha_text = False
    
    return captcha_text