# tensorview
A hyper parameter visualization tool bringing the power of SQL
queries to the task of hyperparameter optimization and analysis.

To be properly functional you must follow the suggested directory structure proposed
at https://github.com/tensorflow/tensorboard and then meaningfully name the runs folders
such that the name reflects what hpyerparameters you wish to track and their corresponding 
values.

The naming convention is as follows:
/some/path/mnist_experiments/hp1-v1_hp2-v2_hp3_v3

where hp is the hyperparameter name and v is the corresponding value.
That is each hpyperparameter value pair is delineated by the dash, and pairs
are separated by an underscore.

This tool is meant to be used in conjunction with Tensorboard.

To see command line arguments use the -h option.

