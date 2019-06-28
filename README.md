# histomicstk Feature Extraction
Scripts to help extract features from nuclei of pathology slides

## Usage
python get_histomics_features.py <path of image to analyze> <path of image to normalize the input image to> <minimum nuclei area in px for an object to be labeled nuclie> <foreground threshold to identify nuclei in grayscale <path of folder where output files should be stored>
  
### Example Usage
python get_histomics_features.py ../prostate_images/T4--33-B6-L_L3R5_T4_22.png ../prostate_images/T4--33_B6_R_L1R6_T4_3.png 15 100 histomics_output/

## Output files
<file_name>-Normalization.png - Reference and normalized image

<file_name>-Nuclei.png - Nuclei highlighted and bounding boxes in input image

<file_name>-Stains.png - Eosin and Hematoxylin Stains

<file_name>-eosin.png - Eosin Stain

<file_name>-hematoxylin.png - Hematoxylin Stain

<file_name>-fsd.csv - Fourier shape descriptors for all nucleis

<file_name>-gradient.csv - Gradient Features for all nucleis

<file_name>-haralick.csv - Haralick features for all nucleis

<file_name>-morpho.csv - Morphometry Features for all nucleis

### Source and explanation of all features
https://digitalslidearchive.github.io/HistomicsTK/histomicstk.features.html
  
