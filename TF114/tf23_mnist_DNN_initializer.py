import tensorflow as tf
from tensorflow.keras.datasets import mnist
import numpy as np
r = np.random.randint(1,1000)
r = 21
tf.set_random_seed(r)
np.random.seed(r)

(x_train,y_train),(x_test,y_test) = mnist.load_data()
print(x_train.shape,x_test.shape,y_train.shape,y_test.shape)
# (60000, 28, 28) (10000, 28, 28) (60000,) (10000,)
print(np.unique(y_train,return_counts=True))
# (array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=uint8), array([5923, 6742, 5958, 6131, 5842, 5421, 5918, 6265, 5851, 5949],
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
y_train = OneHotEncoder(sparse=False).fit_transform(y_train.reshape(-1,1))
y_test = OneHotEncoder(sparse=False).fit_transform(y_test.reshape(-1,1))

x_train = x_train.reshape(x_train.shape[0],-1)
x_test = x_test.reshape(x_test.shape[0],-1)
print(x_train.shape,x_test.shape,y_train.shape,y_test.shape)
# (60000, 784) (10000, 784) (60000, 10) (10000, 10)

scaler = MinMaxScaler().fit(x_train)
x_train = scaler.transform(x_train)
x_test = scaler.transform(x_test)

x = tf.compat.v1.placeholder(tf.float32,shape=[None,x_train.shape[1]])
y = tf.compat.v1.placeholder(tf.float32,shape=[None,y_train.shape[1]])

""" 
둘이 같다
w1 = tf.compat.v1.Variable(tf.random_normal([input_dim,output_dim]),dtype=tf.float32)
w1 = tf.compat.v1.get_variable('w1',shape=([input_dim,output_dim]),dtype=tf.float32)
"""
class Dense_layer():
    def __init__(self, output_dim, input_dim, activation=None, name=None) -> None:
        with tf.compat.v1.variable_scope(name,reuse=tf.AUTO_REUSE):
            # self.w = tf.compat.v1.get_variable(f'{name}_w',shape=[input_dim,output_dim],initializer=tf.contrib.layers.xavier_initializer())
            self.w = tf.compat.v1.Variable(tf.random_normal([input_dim,output_dim]),dtype=tf.float32)
            self.b = tf.compat.v1.Variable(tf.zeros([1,output_dim]),dtype=tf.float32)
        self.activation = activation
    def get_layer(self,x):
        result = tf.matmul(x,self.w) + self.b
        if self.activation is not None:
            return self.activation(result)
        return result

IS_TRAIN = True
LR = 0.001
layer1 = Dense_layer(128,x_train.shape[1],tf.nn.selu,'d1').get_layer(x)
if IS_TRAIN:
    layer1 = tf.compat.v1.nn.dropout(layer1,keep_prob=0.95)
    # layer1 = tf.compat.v1.nn.batch_normalization(layer1)
layer2 = Dense_layer(128,128,tf.nn.selu,'d2').get_layer(layer1)
if IS_TRAIN:
    layer2 = tf.compat.v1.nn.dropout(layer2,keep_prob=0.95)
    # layer2 = tf.compat.v1.nn.batch_normalization(layer2)
layer3 = Dense_layer(64,128,tf.nn.sigmoid,'d3').get_layer(layer2)
# if IS_TRAIN:
#     layer3 = tf.compat.v1.nn.dropout(layer3,keep_prob=0.95)
layer4 = Dense_layer(64,64,tf.nn.selu,'d4').get_layer(layer3)
# if IS_TRAIN:
#     layer4 = tf.compat.v1.nn.dropout(layer4,keep_prob=0.95)
layer5 = Dense_layer(32,64,tf.nn.selu,'d5').get_layer(layer4)
layer6 = Dense_layer(16,32,tf.nn.sigmoid,'d6').get_layer(layer5)
last_layer = Dense_layer(y_train.shape[1],16,tf.nn.softmax,'last')
hypothesis = last_layer.get_layer(layer6)

loss_fn = tf.compat.v1.losses.softmax_cross_entropy(y,hypothesis)
optimizer = tf.train.AdamOptimizer(learning_rate=LR)

train = optimizer.minimize(loss_fn)

EPOCHS = 2000
BATCH = 8192
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    # batch
    x_train_list = []
    y_train_list = []
    for i in range((x_train.shape[0]//BATCH) +1):
        s = i*BATCH
        e = (i+1)*BATCH
        if e > x_train.shape[0]:
            x_train_list.append(x_train[s:])
            y_train_list.append(y_train[s:])
        else:
            x_train_list.append(x_train[s:e])
            y_train_list.append(y_train[s:e])
    print("x_list, y_list length:",len(x_train_list),len(y_train_list))
    for x_data, y_data in zip(x_train_list,y_train_list):
        print("split by x_data, y_data")
        print(len(x_data),len(y_data))
    
    # Early Stopping
    best_loss = 987654321
    best_setting = {'w':None,'b':None}
    patient_stacking = 0    
    PAITIENT = 10
    import copy
    
    for step in range(1,EPOCHS+1):
        if patient_stacking >= PAITIENT:
            print(f"Early Stop: {step}epos")
            break
        patient_stacking += 1
        
        for x_data ,y_data in zip(x_train_list,y_train_list):
            _, loss, weight, bias = sess.run([train,loss_fn,last_layer.w,last_layer.b], feed_dict={x:x_data,y:y_data})
        if loss < best_loss:
            best_loss = loss
            best_setting = {'w':weight,'b':bias}
            best_layer = hypothesis
            print(f"Best: {step}epo's loss={loss}")#, weight:{weight} bias:{bias}")
            patient_stacking = 0
            
        if step%10 == 0:
            print(f"{step}epo loss={loss}")
            
    IS_TRAIN = False
    predict = sess.run(best_layer,feed_dict={x:x_test})
    pred = np.argmax(predict,axis=1)
    y_test = np.argmax(y_test,axis=1)
    
print("pred: ",pred.shape)
from sklearn.metrics import r2_score, accuracy_score
acc = accuracy_score(pred,y_test)

print("ACC: ",acc)
print("Random state: ",r)

# pred:  (10000, 10)
# ACC:  0.9258
# Random state:  21