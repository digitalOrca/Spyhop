#!/usr/bin/python3

from sklearn.linear_model import SGDRegressor
from Preprocess import Preprocess

class SGDRegression(SGDRegressor):

    def __init__(self, lag=30, density=0.8, dimReductAlgo=None, loss="squared_loss", \
                 penalty="l2", alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=None, \
                 tol=None, shuffle=True, verbose=0, epsilon=0.1, random_state=None, \
                 learning_rate="invscaling", eta0=0.01, power_t=0.25, \
                 warm_start=False, average=False, n_iter=None):
        SGDRegressor.__init__(self, loss=loss, penalty=penalty, alpha=alpha, \
                              l1_ratio=l1_ratio, fit_intercept=fit_intercept, \
                              max_iter=max_iter, tol=tol, shuffle=shuffle, \
                              verbose=verbose, epsilon=epsilon, random_state=random_state, \
                              learning_rate=learning_rate, eta0=eta0, power_t=power_t, \
                                warm_start=warm_start, average=average, n_iter=n_iter)
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, density=density)
        self.dimReductAlgo = dimReductAlgo
    
    
    def prepareData(self, lag = True, dset = "all"):
        scaled_data = self.preprocess.get_data('raw', lag=lag, dset=dset)
        if self.dimReductAlgo is None:
            return scaled_data
        if isinstance(self.dimReductAlgo, PCAImpl):
            self.dimReductAlgo.fit(scaled_data)
            f = scaled_data.as_matrix()
            if dset == "validate" or dset == "all":
                c = np.transpose(np.array(self.dimReductAlgo.getComponents()))
            else:
                c = np.transpose(np.array(self.dimReductAlgo.getComponents(0.99)))
            pc = np.matmul(f, c)
            cols = range(self.dimReductAlgo.numPC)
            reducedData = pd.DataFrame(data=pc, index=scaled_data.index, columns=cols)
            return reducedData
    
        
    def train(self, trainset=None):
        if trainset is not None:
            traindata = trainset
        else:
            traindata = self.prepareData(lag=True, dset="train")
        ret = self.preprocess.compute_return()
        traindata = traindata.join(ret, how="inner")
        y = traindata["return"].copy()
        x = traindata.drop(['return'], axis=1, inplace=False)
        super(SGDRegression, self).fit(x, y)
        return traindata
        
        
    def validate(self, validateset):
        validateset['predict'] = super(SGDRegression, self).predict(validateset)
        return validateset
        
        
    def train_validate(self):
        trainSet, validateSet = self.prepareData(lag=True, dset="train_validate")
        t = self.train(trainset = trainSet)
        v = self.validate(validateset = validateSet)
        return t,v
    
    
    def predict(self):
        df = self.prepareData(lag=False)
        print("predict------>",df.shape)
        for column in df.columns:
            if column not in self.cols:
                df.drop([column], axis=1, inplace=True)
        df['label'] = super(SGDRegression, self).predict(df)
        return df
    
    """
    def getScore():
        return super(SGDRegression, self).score(validateset)
    """
    
sgd = SGDRegression()
sgd.train_validate()
#sgd.predict() 
#TODO: get columns to match the trained matrix


