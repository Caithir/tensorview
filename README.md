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

This tool is meant to be used in conjunction with Tensorboard as it reads the log files tensorboard
outputs, and it provides functionality for generating regexes to view your selected runs in tensorboard.

To see command line arguments use the -h option.

Deployment of the system is easy! Just use pip!

You can pip install on the github url.


# Limitations of Implementation

hyperparameter names should refrain from using the ~ character to prevent
conflicts in the url parsing. Best used with an ultrawide monitor for best 
results as there is not ui rescaling.

# code structure

app.py holds all the functions to handle the url requests.
tables.py contains the code for the controller, and db.py 
holds the code for the model. These are the three core files,
with the crawler being run when requested.