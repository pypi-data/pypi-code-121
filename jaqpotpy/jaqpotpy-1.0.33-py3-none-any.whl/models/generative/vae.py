import ast
from jaqpotpy.datasets import SmilesDataset
from jaqpotpy.descriptors.molecular import MolGanFeaturizer


import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow import keras
from keras import layers

import matplotlib.pyplot as plt
from rdkit import Chem, RDLogger
from rdkit.Chem import BondType
from rdkit.Chem.Draw import MolsToGridImage

RDLogger.DisableLog("rdApp.*")

csv_path = keras.utils.get_file(
    "./250k_rndm_zinc_drugs_clean_3.csv",
    "https://raw.githubusercontent.com/aspuru-guzik-group/chemical_vae/master/models/zinc_properties/250k_rndm_zinc_drugs_clean_3.csv",
)

df = pd.read_csv("/Users/pantelispanka/.keras/datasets/250k_rndm_zinc_drugs_clean_3.csv")
df["smiles"] = df["smiles"].apply(lambda s: s.replace("\n", ""))
print(df.head())

smiles = df['smiles'].to_list()

feat = MolGanFeaturizer(max_atom_count=100)

dataset = SmilesDataset(smiles=smiles, featurizer=feat, task="generation")
dataset = dataset.create()
print(dataset.df)

