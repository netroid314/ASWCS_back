# Rpository Info
this is respository of DAIG (Distributed A.I Grid) project client program.
it is based on PyQT5 because we use tensorflow for model training and others.
- - -
# What is DAIG?
DAIG (Distributed A.I Grid) is distributed deep learning based machine learning system.
Usually, deep learning based machine learning methods require more training time than other methods.
One way to solve this long training time problem is using multiple GPUs. However, it is pretty expensive.
So, we tried to use other people's left pc resources instead of multiple GPUs
- - -
# How DAIG works?
DAIG system consists of Learning requestor, Resource provider and Management server.
Learning requestor makes project and upload train data to Management server.
Then, Management server distribute train data shards and model information to registered Resource providers
When all train data shards are used for leatning, Management server save final model and weight result at object storage.
Learning requestor can download trained model at anytime.

## DAIG structure
![image](https://user-images.githubusercontent.com/22979031/120693675-47bba700-c4e4-11eb-94b6-f079a1ae0f46.png)
![image2](https://user-images.githubusercontent.com/22979031/120912837-895b7600-c6cd-11eb-93a9-890f489ed992.PNG)
- - -
# How DAIG's distribution works?
We constructed DAIG distribution and result gathering system based on K-batch sync SGD.
And it gathers trained gradients based on all-reduce method.
K-batch size can be controlled by Learning requestor.
So, its final result is also contorlled by Learning requestor.
- - -
# How to use DAIG?
This is server program. so, you should better check "https://github.com/netroid314/ASWCS_front"
- - -
# How to launch server?
Use manage.py for Django server launch. One exmaple is 'python manage.py runserver 0.0.0.0:8000'.
Use port number 8000 for default setting.
- - -
# Some points of DAIG server
## One way to treat numpy file via https
## How K-batch sync SGD is established
However, DAIG also focused on balance among Resource providers. so, it may not be pure K-batch sync SGD. (depends on situation)


### Caution!
this project has been developed by korean developers. So, there are some korean comments.
And this is server program so please also check https://github.com/netroid314/ASWCS_front.
