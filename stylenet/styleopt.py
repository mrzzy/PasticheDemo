#
# styleopt.py
# Artistic Style Transfer 
# Optimisation method
# as defined in Gatys et. al
#

import os
import numpy as np
import tensorflow as tf
import keras.backend as K
import stylefn

from PIL import Image
from keras.models import Model, Sequential
from shutil import rmtree
from tensorflow.contrib.opt import ScipyOptimizerInterface
from datetime import datetime

# Perform style transfer using the optimisation method on the given content image 
# using the style from the given style image. Images are rescaled to image_size 
# before performing style transfer
# Optimise for the given number epochs. If verbose is True, will output training
# progress infomation to standard output
# Returns the pastiche, the results of performing style transfer
K.set_learning_phase(0)
def transfer_style(content_image, style_image, n_epochs=100, image_size=(512, 512),
                   verbose=False):
    #TODO: add progressive style transfer
    # Update style parameters
    stylefn.SETTINGS["image_shape"] = image_size + (3,)
    
    # Preprocess image data
    content = stylefn.preprocess_image(content_image)
    style = stylefn.preprocess_image(style_image)
    pastiche = content.copy() # Generate pastiche from content
    
    # Setup input tensors
    pastiche_op = K.variable(pastiche, name="pastiche")
    content_op = K.constant(content, name="content")
    style_op = K.constant(style, name="style")

    # Build style transfer graph
    loss_op = stylefn.build_loss(pastiche_op, content_op, style_op)
    
    # Perform style transfer by optimising style transfer loss
    session = tf.Session()
    K.set_session(session)

    optimizer = tf.train.AdamOptimizer(learning_rate=3e+1)
    train_op = optimizer.minimize(loss_op, var_list=[pastiche_op])

    # Setup tensorboard
    summary_op = tf.summary.merge_all()
    if verbose: 
        writer = tf.summary.FileWriter("logs/{}".format(datetime.now()), session.graph)

    session.run(tf.global_variables_initializer())
    for i in range(1, n_epochs + 1):
        _, loss, pastiche = session.run([train_op, loss_op, pastiche_op])
        # Display progress infomation and record data for tensorboard
        if verbose: 
            print("[{}/{}] loss: {:e}".format(i, n_epochs, loss), end="\r")
            summary = session.run(summary_op)
            writer.add_summary(summary, i)
    
    # Deprocess style transfered image
    pastiche_image = stylefn.deprocess_image(pastiche)
    return pastiche_image

if __name__ == "__main__":
    content_image = Image.open("data/Tuebingen_Neckarfront.jpg")
    style_image = Image.open("data/stary_night.jpg")
    pastiche_image = transfer_style(content_image, style_image, verbose=True)
    
    pastiche_image.save("pastiche.jpg")
