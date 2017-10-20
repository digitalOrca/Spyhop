#!/usr/bin/python

from LinearRegression import LinearRegression
from KMeansImpl import KMeansImpl

lr = LinearRegression()
lr_train, lr_validate = lr.train_validate("snp500")
lr_predict = lr.predict()
print lr_predict

kmi = KMeansImpl(dimReductAlgo='PCA')
kmi_train, kmi_validate = kmi.train_validate()
kmi_predict = kmi.predict()
print kmi_predict

overall_train = lr_train.join(kmi_train['label'], how='inner')
print overall_train

for cluster in range(kmi.n_clusters):
    avgRet = overall_train[overall_train["label"]==cluster]["return"].mean(skipna=True)
    if cluster == 0:
        bestCluster = cluster
        bestReturn = avgRet
    if avgRet > bestReturn:
        bestCluster = cluster
        bestReturn = avgRet
    
    c = overall_train[overall_train["label"]==cluster]
    rate = 1.0 - float((c["return"]<0).sum())/float(len(c["return"]))
    print "cluster:",cluster," average return:","%6f"%overall_train[overall_train["label"]==cluster]["return"].mean(skipna=True)," rate:",rate
    
print overall_train[overall_train["label"]==bestCluster]

overall_predict = lr_predict.to_frame().join(kmi_predict['label'], how='inner')

print "=============================================="
print lr_validate
print kmi_validate





#TODO: investigate variance difference between cluster_weight
#TODO: investigate number of negatives in each cluster

#print overall_train
#print overall_predict


#result #Compile score ranking prediction with cluster prediction

#n_clusters = 4
#cluster_weight = [0.25,0.25,0.25,0.25]
#n_stocks = 50

#for cluster in range(n_clusters):
    #select 50*0.25 top row for cluster 1,2,3,4
    
    
#average ar for all selected stock

#return averaged return as fitness
    #maybe regularize with the consistency of the return
