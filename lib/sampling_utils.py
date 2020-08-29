import sys
import os
from glob import glob
import pydicom
import zarr
import numpy as np
import pandas as pd
import random
import skimage
from skimage.filters import threshold_otsu
from scipy.signal import find_peaks

def get_lung_location(img,slice_axes=(0,1)):
    ''' Finds start and end slice index for a 3d image based on foreground pixel sum in each slice
    '''
    thresh = threshold_otsu(img)
    img_binary = img > thresh
    slice_sum = np.sum(img_binary,axis=slice_axes)
    peaks, _ = find_peaks(slice_sum, height=np.mean(slice_sum))
    start_slice_idx = np.min(peaks)
    end_slice_idx = np.max(peaks)
    endpoints = [start_slice_idx,end_slice_idx]
    
    return slice_sum, endpoints
    
    
def get_slice_locations(CT_endpoints,n_CT_partitions,n_samples_per_scan):
    ''' Samples slices from a start-end slices range for list of CT scans.
        Samples are chosen evenly across given number of partitions of the range.
    '''
    n_CT_scans = len(CT_endpoints)
    
    assert n_samples_per_scan > n_CT_partitions #don't want to undersample
    
    n_samples_per_CT_partitions = n_samples_per_scan//n_CT_partitions
        
    print('Number of CT scans {}, CT_partitions: {}, samples per scan: {},\
    n_samples_per_CT_partitions: {}'.format(n_CT_scans, n_CT_partitions, n_samples_per_scan,
    n_samples_per_CT_partitions))
    
    sample_df = pd.DataFrame()
    for CT_id, CT_endpoints in CT_endpoints.items():
        n_available_slices = CT_endpoints[1] - CT_endpoints[0]
        assert n_available_slices > n_samples_per_scan #don't want to repeat samples
        sample_ids_dict = sample_paritions(CT_endpoints, n_CT_partitions, n_samples_per_CT_partitions)

        df = pd.DataFrame()
        df['CT_id'] = np.repeat(CT_id,n_CT_partitions)
        df['partition_id'] = list(sample_ids_dict.keys())
        df['slice_ids'] = list(sample_ids_dict.values())
        
        sample_df = sample_df.append(df)
        
    return sample_df

def sample_paritions(endpoints, n_partitions, n_samples_per_partition,random_seed=153):
    ''' Partitions a given range in similar sized chunks and and samples from each. 
    '''
    partitions = np.array_split(np.arange(endpoints[0],endpoints[1]),n_partitions)
    sample_ids_dict = {}
    random.seed(random_seed)
    for p, part in enumerate(partitions):
        sample_ids = random.sample(list(part),n_samples_per_partition)
        sample_ids_dict[p] = sample_ids
        
    return sample_ids_dict
        