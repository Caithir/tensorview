import os
import tensorflow as tf

def _get_parent_name(dirpath):
    parentdir = os.path.abspath(os.path.join(dirpath, os.pardir))
    return os.path.basename(parentdir)

# Convention: pname1-pval1_pname2-pval2_..._pnamen-pvaln
def _parse_dir(dirname):
    dirname = os.path.basename(dirname)
    pmap = {}

    params = dirname.split('_')
    for p in params:
        p = p.split('-')
        pname, pval = p[0], p[1]
        # Convert to float if applicable
        try:
            pval = float(pval)
        except:
            pass
        pmap[pname] = pval

    return pmap

# Crawl through training data to extract relevant parameter names
def crawl(rootdir):
    parameters = {}

    for dirname, subdirlist, filelist in os.walk(rootdir):
        exp = _get_parent_name(dirname)

        for fname in filelist:
            if exp not in parameters:
                parameters[exp] = {}

            fpath = os.path.join(dirname, fname)
            tags = {}

            # Add hyper parameters from directory name (pre-determined convention)
            hyperparams = _parse_dir(dirname)

            tags.update(hyperparams)

            # Add dependent parameters from tfevent protobuf as key and the most recent value
            for e in tf.train.summary_iterator(fpath):
                for v in e.summary.value:
                    if v.tag not in tags:
                        tags[v.tag] = []
                    tags[v.tag] += [v.simple_value]

            parameters[exp][fname] = tags

    return parameters
