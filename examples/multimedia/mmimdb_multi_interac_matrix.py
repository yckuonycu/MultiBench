import sys
import os
sys.path.append(os.getcwd())
from training_structures.Simple_Late_Fusion import train, test
from fusions.common_fusions import MultiplicativeInteractions2Modal
from datasets.imdb.get_data import get_dataloader
from unimodals.common_models import MaxOut_MLP, Linear
from torch import nn
import torch

traindata, validdata, testdata = get_dataloader('../video/multimodal_imdb.hdf5', vgg=True, batch_size=128)
encoders=[MaxOut_MLP(512, 512, 300, linear_layer=False), MaxOut_MLP(512, 1024, 4096, 512, False)]
head= Linear(1024, 23).cuda()

fusion=MultiplicativeInteractions2Modal([512,512],1024,'matrix').cuda()

train(encoders,fusion,head,traindata,validdata,1000, early_stop=True,task="multilabel", regularization=False,\
    save="best_mim.pt", optimtype=torch.optim.AdamW,lr=8e-3,weight_decay=0.01, criterion=torch.nn.BCEWithLogitsLoss())

print("Testing:")
model=torch.load('best_mim.pt').cuda()
test(model,testdata,dataset='imdb',criterion=torch.nn.BCEWithLogitsLoss(),task="multilabel")


