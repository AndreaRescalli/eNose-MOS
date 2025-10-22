# MOS V2 - Single Compounds and Mixture of Compounds

## Feature Extraction
The first step for the analysis is the extraction of features. The following script must be run to extract the features:
1. [Single Compounds Feature Extraction](feature_extraction.py): This script extracts features from the responses of the sensors when exposed to single compounds. This script outputs a file called ``single_compounds_features.csv`` in the ``Outputs`` folder, containing the extracted features.
2. [Compounds Mixture Feature Extraction](feature_extraction_mixtures.py): This script extracts features from the responses of the sensors when exposed to mixtures of compounds. This script outputs a file called ``compound_mixtures_features.csv`` in the ``Outputs`` folder, containing the extracted features.

## Data Analysis
1. [Single Compounds](sensors_pca_single.py): This script performs a Principal Component Analysis (PCA) on the features extracted from the sensors when exposed to single compounds, and saves the resulting components into a file called ``single_pca.pkl`` in the ``Outputs`` folder. On top of this, the script also performs Linear Discriminant Analysis (LDA) on the same set of features, and save the resulting LD components in a file called ``single_lda.pkl`` in the ``Outputs`` folder.
2. [Compounds Mixtures](sensors_pca_mix.py): This scripts uses the previously extracted principal components (PC) and applies them to the features extracted from the sensors when exposed to the mixture of compounds, and on top of this it also performs PCA and LDA directly on the features extracted from the mixtures of compounds. 

## Notebooks
The following notebooks are also available
- [Analysis of Single Compounds](Notebooks/01_SingleCompoundsAnalysis.ipynb) Visualization of features extracted from sensors when exposed to single compounds
- [Analysis of Compounds Mixtures](Notebooks/02_MixturesAnalysis.ipynb) Visualization of features extracted from sensors when exposed to mixtures of compounds
