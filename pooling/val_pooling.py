from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.metrics import confusion_matrix
from torchvision import transforms, models
from sklearn.metrics import accuracy_score
from sklearn.manifold import TSNE
from PIL import Image
from torch import nn
import pandas as pd
import numpy as np
import argparse
import random
import torch
import time
import copy
import os

from dataloader import *
from utils import *

import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
os.environ["CUDA_VISIBLE_DEVICES"] = "5"



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder_name', type = str, required = True)
    args = parser.parse_args()
    
    records_dir = args.folder_name  
    os.mkdir(f"{records_dir}/results")
    results_dir = f"{records_dir}/results"

    with open(f"./{records_dir}/valimages.txt", "r") as f:
        image_names = f.read().splitlines()
    image_names = [i for i in image_names if ".ipynb" not in i]

    data = Valoader(image_names, "../../clean_data/wealth_random_points_cumsum_jenks.csv", records_dir)

    device = "cuda"
    model_ft = models.resnet50(pretrained = True)
    num_ftrs = model_ft.fc.in_features
    model_ft.fc = nn.Linear(num_ftrs, 4)
    model_ft = model_ft.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer_ft = torch.optim.Adam(model_ft.parameters(), lr=0.0001)
    exp_lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)  
    
    
    saved_models = [i for i in os.listdir(records_dir + "/models/") if i != "records.txt"]
    saved_models = [i for i in saved_models if ".ipynb" not in i]
    saved_models = [i for i in saved_models if ".sav" not in i]
    weights = records_dir + "/models/" + saved_models[-1]
    print(weights)    

    testm = torch.load(weights)["model_state_dict"]
    model_ft.load_state_dict(testm)
    model_ft.eval();
    
    
    preds, trues, ids = [], [], []
    
    for i in range(len(image_names)):
        try:
            inp, out = data.load_data(i)
            print(inp.shape)
            inp, out = inp.to(device), out.to(device)
            pred = torch.max(model_ft(inp), 1)[1]
            print(pred.item())
            trues.append(out.item())
            preds.append(pred.item())
            ids.append(image_names[i])
        except:
            pass
        
df = pd.DataFrame()
df["school_id"] = ids
df["pred"] = preds
df["true"] = trues
print(df.head())

acc = accuracy_score(df["true"], df["pred"])
cm = pd.DataFrame(confusion_matrix(df["true"], df["pred"]))

print("Accuracy Score: ", acc)
print(cm)

df.to_csv(f"{records_dir}/results/preds.csv", index = False)
cm.to_csv(f"{records_dir}/results/cm.csv", index = False)
