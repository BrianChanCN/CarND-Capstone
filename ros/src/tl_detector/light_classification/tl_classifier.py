from styx_msgs.msg import TrafficLight
from keras.preprocessing.image import img_to_array
import numpy as np
import keras.backend as K
from squeezenet import SqueezeNet
from consts import IMAGE_WIDTH, IMAGE_HEIGHT
import rospy
import cv2
import os
import tensorflow as tf
from keras.models import load_model

# Model vgg16_trafficlight_simulator_model -> https://drive.google.com/open?id=0B5_xbblUg-gDR1FNUmRGekdNRFE

class TLClassifier(object):
    def __init__(self):
        rospy.loginfo("TLClassifier starting")
        K.set_image_dim_ordering('tf')
        self.model = SqueezeNet(3, (IMAGE_HEIGHT, IMAGE_WIDTH, 3))
        fname = os.path.join('light_classification', 'trained_model/challenge1.weights')
        # self.model = load_model(fname)
        # self.model = load_model(fname)
        self.model.load_weights(fname)
        self.graph = tf.get_default_graph()
        # self.debug_img_counter = 1

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        # save

        # self.debug_img_counter = self.debug_img_counter + 1
        # cv2.imwrite('image{0}.png'.format(self.debug_img_counter), image)
        image = image.astype(dtype=float)
        # print(image)
        rospy.loginfo("TLClassifier get_classification")
        image = cv2.resize(image, (IMAGE_HEIGHT, IMAGE_WIDTH))
        # print(image.__shape__)
        # image = np.asarray(image)
        image /= 255.0
        image = np.expand_dims(image, axis=0)
        with self.graph.as_default():
            preds = self.model.predict(image)[0]
        prediction_result = int(np.argmax(preds))

        rospy.loginfo("Traffic light: {0}".format(prediction_result))
        # print(prediction_result.__class__)

        if prediction_result == 0:
            rospy.loginfo('tl_classifier: red traffic light detected')
            # print("RED")
            return TrafficLight.RED
        elif prediction_result == 2:
            rospy.loginfo('tl_classifier: Green traffic light detected.')
            # print("GREEN")
            return TrafficLight.GREEN
        else:
            rospy.loginfo('tl_classifier: Unknown traffic light detected')
            # print("UNKNOWN")
            return TrafficLight.UNKNOWN
