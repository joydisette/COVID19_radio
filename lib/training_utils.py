import numpy as np
import pandas as pd
import sys
import os
import pickle
from sklearn.model_selection import StratifiedKFold
from tensorflow import keras
from tensorflow.keras import layers

def get_slice(slice_id,slice_shape):
    #TODO
    img = np.random.rand(slice_shape[0],slice_shape[1])
    return img
    
def batch_generator(CT_ids, metadata_df, data_subset, slice_shape, num_classes, data_aug_config=None):
    # May need to balance slice_label if there is large imbalance from random sampling of CT scans. 
    
    ''' Generator for creating training or testing batches
        Parameters
        ----------
        CT_ids: list
            list of scan IDs (e.g. CT IDs)
            
        data_subset: str
            'train' or 'test'
            
        data_aug_config: dict
            data augmentation configs for brightness adjustment and image flips
        
        Returns
        -------
        batch_x, batch_y
            batch of paired image and label patches
    '''
   
    while True:
        slice_image_list = []
        slice_label_list = []
        
        # Iterate thru CT scans
        for CT_id in CT_ids:
            scan_df = metadata_df[metadata_df['CT_id']==CT_id]
            slice_ids = scan_df['slice_id'].values
            slice_labels = scan_df['slice_label'].values
            
            # Iterate thru slices within a scan
            for slice_id,slice_label in zip(slice_ids,slice_labels):
                slice_image_list.append(get_slice(slice_id,slice_shape))
                slice_label_list.append(slice_label)
        
        # Reshape for keras
        slice_image_list = np.expand_dims(np.array(slice_image_list), axis=-1)
        slice_label_list = keras.utils.to_categorical(slice_label_list, num_classes)
        
        yield ( slice_image_list, slice_label_list )