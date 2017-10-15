#!/usr/bin/python

from LinearRegression import LinearRegression
from KMeanImpl import KMeanImpl


lr = LinearRegression()
lr_train = lr.fit("snp500")
lr_predict = lr.predict()
print lr_predict

kmi = KMeanImpl()
kmi_predict = kmi.fit_predict('PCA')
print kmi_predict

overall_predict = lr_predict.to_frame().join(kmi_predict['label'], how='inner')



#result #Compile score ranking prediction with cluster prediction

#n_clusters = 4
#cluster_weight = [0.25,0.25,0.25,0.25]
#n_stocks = 50

#for cluster in range(n_clusters):
    #select 50*0.25 top row for cluster 1,2,3,4
    
    
#average ar for all selected stock

#return averaged return as fitness
    #maybe regularize with the consistency of the return
