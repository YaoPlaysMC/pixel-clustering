from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.tree import DecisionTreeRegressor
from random import randint

white_threshold = 730
max_pixels = 199999 # prime
# Change algorithm to go from using most common labels to using average color of each pixel
# Cache cluster models and pixel counts
# Add gui with pyside6
# add filter for variance in range

# Note to self: OP resume fodder
# Port to web
# Deploy on streamlit

def slice_array(shape, pixel_size):
    num_x, num_y = pixel_size
    for y in range(num_y):
        # temp = []
        for x in range(num_x):
            min_x = shape[1] * x // num_x
            min_y = shape[0] * y // num_y
            max_x = shape[1] * (x+1) // num_x
            max_y = shape[0] * (y+1) // num_y
            yield min_x, min_y, max_x, max_y

# TODO: Document functions
#
def get_new_path(path, num_colors, mode):
    array = list(path.split("."))
    array[-2] += "_" + mode + "_" + str(num_colors)
    return ".".join(array)

#DOne on every element of the hs array
def polar_to_rectangular(hs_array):
    theta = (np.pi/128)*hs_array[:,0]
    r = hs_array[:,1]
    
    # print(theta,r)
    x = np.cos(theta) * r
    y = np.sin(theta) * r
    return np.stack((x, y), 1)

#Done on 
def rectangular_to_polar(array):
    temp = []
    for x, y in array:
        # print(str(x) + " :skull: " + str(y))
        if y == 0:
            if x >= 0:
                temp.append([64, x])
            else:
                temp.append([192, -x])
        else:
            hue = np.arctan(y / x)*128/np.pi
            if hue < 0:
                hue += 128
            if y < 0:
                hue += 128
            temp.append([hue,np.sqrt(x ** 2 + y ** 2)])
    return np.array(temp)
        

def cluster_image(image, num_colors, mode="rgb", algorithm="KMeans", 
        filter_white = False, smooth_color_frequency = False, pixel_size = None):
    # image = Image.open(path)
    if mode == "rgb":
        image = image.convert("RGB")
    elif mode in ["hsv", "h_sv"]:
        image = image.convert("HSV")
    else:
        raise ValueError("Mode is not one of the allowed modes")
    
    img_array = np.asarray(image)
    # new_path = get_new_path(path, num_colors, mode)
    shape = img_array.shape
    num_pixels = img_array.shape[0] * img_array.shape[1]
    flat_array = img_array.reshape(num_pixels, img_array.shape[2])
    
    #sort array is array used for clustering
    #fixed array contains other attributes
    sort_array = fixed_array = np.array([])
    if mode == "rgb":
        sort_array = flat_array
    elif mode == "hsv":
        sort_array = flat_array[:,1:3]
        fixed_array = flat_array[:,0:1]
    elif mode == "h_sv":
        sort_array = polar_to_rectangular(flat_array[:,0:2])
        fixed_array = flat_array[:,2:3]
    elif mode == "positional":
        pass
    
    if algorithm == "KMeans":
        # if mode == "supervised":
        #     raise ValueError
        k_means = KMeans(num_colors)
        
        
        if smooth_color_frequency:
            unique_array, weights = np.unique(sort_array, return_counts=True, axis=0)
            weights = np.sqrt(weights)
            k_means.fit(unique_array, sample_weight=weights)
        else:
            indices = np.arange(num_pixels)
            shrunk_sort_array = sort_array[indices * max_pixels % num_pixels < max_pixels]
            k_means.fit(shrunk_sort_array)
        
        centers = k_means.cluster_centers_
        
        #average out sort_array
        if pixel_size != None:
            curr = sort_array.reshape(shape[0], shape[1], sort_array.shape[1]).copy()
            for min_x, min_y, max_x, max_y in slice_array(shape, pixel_size):
                    slice = curr[min_y:max_y,min_x:max_x]
                    # print(slice.sum(axis=(0,1)) // (np.size(slice, axis=(0,1))))
                    # 1/0
                    curr[min_y:max_y,min_x:max_x] = slice.sum(axis=(0,1)) // np.size(slice, axis=(0,1))
                    # print(slice.sum(axis=(0,1)) / slice.size / 3)
                    # print(f"[{min_y}:{max_y},{min_x}:{max_x}]")
            sort_array = curr.reshape(num_pixels, sort_array.shape[1])
        
        labels = k_means.predict(sort_array)
        
        if mode == "h_sv":
            centers = rectangular_to_polar(centers)
            
    
        
        if pixel_size != None:
            # labels = np.array(labels).reshape(*shape[:2])
            # # print(labels.shape)
            # for min_x, min_y, max_x, max_y in slice_array(shape, pixel_size):
            #     slice = labels[min_y:max_y,min_x:max_x].flatten()
            #     top = np.bincount(slice).argmax()
            #     labels[min_y:max_y,min_x:max_x] = top
            # labels = labels.reshape(num_pixels)
            temp_array = centers[labels]
                    
            if fixed_array.size != 0:
                if mode == "h_sv":
                    curr = fixed_array.reshape(*shape[:2]).copy()
                    for min_x, min_y, max_x, max_y in slice_array(shape, pixel_size):
                            slice = curr[min_y:max_y,min_x:max_x]
                            curr[min_y:max_y,min_x:max_x] = slice.sum() / slice.size
                    fixed_array = curr.reshape(num_pixels, 1)
                elif mode == "hsv":
                    curr = fixed_array.reshape(*shape[:2]).copy()
                    for min_x, min_y, max_x, max_y in slice_array(shape, pixel_size):
                            slice = curr[min_y:max_y,min_x:max_x]
                            curr[min_y:max_y,min_x:max_x] = slice[randint(0, max_y-min_y-1), randint(0, max_x-min_x-1)]
                    fixed_array = curr.reshape(num_pixels, 1)
        else:
            temp_array = centers[labels]
        # restored_array = temp_array
        if mode == "hsv":
            temp_array = np.concatenate((fixed_array, temp_array), axis=1)
        elif mode == "h_sv":
            temp_array = np.concatenate((temp_array, fixed_array), axis=1)
    elif algorithm == "tree":
        
        tree = DecisionTreeRegressor(max_leaf_nodes=num_colors)
        # predict color from position
        if mode == "rgb":
            pass
        # elif mode == h_sv
        raise NotImplementedError
    else:
        raise ValueError("Invalid Algorithm")
    
    
    
    restored_array = temp_array.reshape(*shape).astype(np.uint8)
    # new_image = None
    if mode == "rgb":
        new_image = new_img = Image.fromarray(restored_array)
    elif mode in ["hsv", "h_sv"]:
        new_image = Image.fromarray(restored_array, mode="HSV").convert('RGB')
    else:
        raise RuntimeError
    # new_image.show()
    return new_image
        
# cluster_image("2tc/neko.jpg", 8, "rgb", pixel_size=(96, 132))
# cluster_image("2tc/assassin.jpg", 8, "rgb").show()
# cluster_image("2tc/atoll_bikini.jpg", 16, "rgb", pixel_size=(128, 187))
# cluster_image("2tc/crystal.jpg", 16, "rgb", pixel_size=(96, 128))
# cluster_image("2tc/press.jpg", 12, "rgb", pixel_size=(128, 187))
# cluster_image("2tc/press.jpg", 16, "rgb", pixel_size=(128, 187))
# cluster_image("2tc/dou_ke_yi.jpg", 4, "rgb", pixel_size=(128, 187))
# cluster_image("2tc/press.jpg", 4, "h_sv", pixel_size=(128, 187))
# bear = polar_to_rectangular(np.array([[0, 0], [64, 100], [160, 100], [192, 100]]))
# print(rectangular_to_polar(bear))


