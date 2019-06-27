import matplotlib
matplotlib.use('Agg')
import histomicstk as htk
import os
import numpy as np
import scipy as sp

import skimage.io
import skimage.measure
import skimage.color

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import sys

file1 = sys.argv[1]
normfile = sys.argv[2]
min_nuc_area = int(sys.argv[3])
fg_thresh = int(sys.argv[4])
out_file = sys.argv[5]
just_name = os.path.splitext(os.path.basename(file1))[0]
plt.rcParams['figure.figsize'] = 10, 10
plt.rcParams['image.cmap'] = 'gray'
titlesize = 24
input_image_file = (file1)  # Easy1.png

im_input = skimage.io.imread(input_image_file)[:, :, :3]
ref_image_file = (normfile)  # L1.png

im_reference = skimage.io.imread(ref_image_file)[:, :, :3]

# get mean and stddev of reference image in lab space
mean_ref, std_ref = htk.preprocessing.color_conversion.lab_mean_std(im_reference)

# perform reinhard color normalization
im_nmzd = htk.preprocessing.color_normalization.reinhard(im_input, mean_ref, std_ref)

# Display results
plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1)
plt.imshow(im_reference)
_ = plt.title('Reference Image', fontsize=titlesize)

plt.subplot(1, 2, 2)
plt.imshow(im_nmzd)
_ = plt.title('Normalized Input Image', fontsize=titlesize)
plt.savefig(out_file+just_name+"-Normalization.png")

####

# create stain to color map
stain_color_map = htk.preprocessing.color_deconvolution.stain_color_map
#print('stain_color_map:', stain_color_map, sep='\n')

# specify stains of input image
stains = ['hematoxylin',  # nuclei stain
          'eosin',        # cytoplasm stain
          'null']         # set to null if input contains only two stains

# create stain matrix
W = np.array([stain_color_map[st] for st in stains]).T

# create initial stain matrix
W_init = W[:, :2]

# Compute stain matrix adaptively
sparsity_factor = 0.5

I_0 = 255

im_sda = htk.preprocessing.color_conversion.rgb_to_sda(im_nmzd, I_0)
W_est = htk.preprocessing.color_deconvolution.separate_stains_xu_snmf(
    im_sda, W_init, sparsity_factor,
)

# perform sparse color deconvolution
imDeconvolved = htk.preprocessing.color_deconvolution.color_deconvolution(
    im_nmzd,
    htk.preprocessing.color_deconvolution.complement_stain_matrix(W_est),
    I_0,
)

#print('Estimated stain colors (in rows):', W_est.T, sep='\n')

# Display results
for i in 0, 1:
    plt.figure()
    plt.imshow(imDeconvolved.Stains[:, :, i])
    _ = plt.title(stains[i], fontsize=titlesize)
    plt.savefig(out_file+just_name+"-"+stains[i]+".png")
####

# create stain to color map
stainColorMap = {
    'hematoxylin': [0.65, 0.70, 0.29],
    'eosin':       [0.07, 0.99, 0.11],
    'dab':         [0.27, 0.57, 0.78],
    'null':        [0.0, 0.0, 0.0]
}

# specify stains of input image
stain_1 = 'hematoxylin'   # nuclei stain
stain_2 = 'eosin'         # cytoplasm stain
stain_3 = 'null'          # set to null of input contains only two stains

# create stain matrix
W = np.array([stainColorMap[stain_1],
              stainColorMap[stain_2],
              stainColorMap[stain_3]]).T

# perform standard color deconvolution
im_stains = htk.preprocessing.color_deconvolution.color_deconvolution(im_nmzd, W).Stains

# Display results
plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1)
plt.imshow(im_stains[:, :, 0])
plt.title(stain_1, fontsize=titlesize)

plt.subplot(1, 2, 2)
plt.imshow(im_stains[:, :, 1])
_ = plt.title(stain_2, fontsize=titlesize)
plt.savefig(out_file+just_name+"-Stains.png")

# get nuclei/hematoxylin channel
im_nuclei_stain = imDeconvolved.Stains[:, :, 0]

# segment foreground
foreground_threshold = fg_thresh

im_fgnd_mask = sp.ndimage.morphology.binary_fill_holes(
    im_nuclei_stain < foreground_threshold)

# run adaptive multi-scale LoG filter
min_radius = 5
max_radius = 10

im_log_max, im_sigma_max = htk.filters.shape.cdog(
    im_nuclei_stain, im_fgnd_mask,
    sigma_min=min_radius/np.sqrt(2),
    sigma_max=max_radius/np.sqrt(2)
)

# detect and segment nuclei using local maximum clustering
local_max_search_radius = 10

im_nuclei_seg_mask, seeds, maxima = htk.segmentation.nuclear.max_clustering(
    im_log_max, im_fgnd_mask, local_max_search_radius)

# filter out small objects
min_nucleus_area = min_nuc_area

im_nuclei_seg_mask = htk.segmentation.label.area_open(
    im_nuclei_seg_mask, min_nucleus_area).astype(np.int)

# compute nuclei properties
objProps = skimage.measure.regionprops(im_nuclei_seg_mask)
print 'Number of nuclei = ', len(objProps)

# calculate features
df1 = htk.features.compute_fsd_features(im_nuclei_seg_mask)
df2 = htk.features.compute_gradient_features(im_nuclei_seg_mask,im_nuclei_stain)
df3 = htk.features.compute_morphometry_features(im_nuclei_seg_mask)
df4 = htk.features.compute_haralick_features(im_nuclei_seg_mask,im_nuclei_stain)
df1.to_csv(out_file+just_name+"-fsd.csv", sep='\t')
df2.to_csv(out_file+just_name+"-gradient.csv", sep='\t')
df3.to_csv(out_file+just_name+"-morpho.csv", sep='\t')
df4.to_csv(out_file+just_name+"-haralick.csv", sep='\t')

# Display results
#sp.misc.imsave("overlav.png",skimage.color.label2rgb(im_nuclei_seg_mask, im_input, bg_label=0))

plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1)
plt.imshow(skimage.color.label2rgb(im_nuclei_seg_mask, im_input, bg_label=0), origin='lower')
plt.title('Nuclei segmentation mask overlay', fontsize=titlesize)
plt.subplot(1, 2, 2)
plt.imshow( im_input )
plt.xlim([0, im_input.shape[1]])
plt.ylim([0, im_input.shape[0]])
plt.title('Nuclei bounding boxes', fontsize=titlesize)

for i in range(len(objProps)):

    c = [objProps[i].centroid[1], objProps[i].centroid[0], 0]
    width = objProps[i].bbox[3] - objProps[i].bbox[1] + 1
    height = objProps[i].bbox[2] - objProps[i].bbox[0] + 1

    cur_bbox = {
        "type":        "rectangle",
        "center":      c,
        "width":       width,
        "height":      height,
    }

    plt.plot(c[0], c[1], 'g+')
    mrect = mpatches.Rectangle([c[0] - 0.5 * width, c[1] - 0.5 * height] ,
                               width, height, fill=False, ec='g', linewidth=2)
    plt.gca().add_patch(mrect)
    
plt.savefig(out_file+just_name+"-Nuclei.png")
