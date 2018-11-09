import os
import tensorflow as tf

# Convention: pname1-pval1_pname2-pval2_..._pnamen-pvaln
def parse_dir(dirname):
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
        for fname in filelist:
            fpath = os.path.join(dirname, fname)
            tags = {}

            # Add hyper parameters from directory name (pre-determined convention)
            hyperparams = parse_dir(dirname)
            tags.update(hyperparams)

            # Add dependent parameters from tfevent protobuf as key and the most recent value
            for e in tf.train.summary_iterator(fpath):
                for v in e.summary.value:
                    tags[v.tag] = v.simple_value

            parameters[fname] = tags

    return parameters

# Temp
def pretty_print(map):
    def recurse(map, prefix):
        if type(map) is dict:
            for item in map:
                print(prefix + item)
                recurse(map[item], prefix + "  ")
        else:
            print(prefix + str(map))

    recurse(map, "")

pretty_print(crawl('./test_data'))