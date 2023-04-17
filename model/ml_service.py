import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import resnet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
redis_db_id = settings.REDIS_DB_ID
redis_host = settings.REDIS_IP
redis_port = settings.REDIS_PORT

db = redis.Redis(host=redis_host, port=redis_port, db=redis_db_id)

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = resnet50.ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    
    # TODO
    img = image.load_img(os.path.join(settings.UPLOAD_FOLDER,image_name), target_size=(224, 224))
    x = image.img_to_array(img)
    x_batch = np.expand_dims(x, axis=0)
    x_batch = resnet50.preprocess_input(x_batch)
    preds = model.predict(x_batch)
    res=resnet50.decode_predictions(preds, top=1)

    prediction = res[0][0][1]
    score = round(float(res[0][0][2]),4)

    return prediction, score

def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        # Get the next job from the Redis queue
        queue_name, job_data = db.brpop(settings.REDIS_QUEUE)

        # Decode the job data from bytes to string
        job_data = json.loads(job_data)

        # Run the ML model on the given data
        prediction, score = predict(job_data["image_name"])

        # Create a dictionary with the prediction and score
        result_dict = {
            'prediction': prediction,
            'score': score
        }

        # Store the results on Redis using the original job ID as the key
        id = job_data["id"]
        db.set(id, json.dumps(result_dict))

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
