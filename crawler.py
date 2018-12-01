import os
import tensorflow as tf
from collections import defaultdict


class Crawler:

    def _get_parent_name(self, dirpath):
        parentdir = os.path.abspath(os.path.join(dirpath, os.pardir))
        return os.path.basename(parentdir)

    # Convention: pname1-pval1_pname2-pval2_..._pnamen-pvaln
    def _parse_dir(self, dirname):
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
    def crawl(self, rootdir):
        experiments = defaultdict(dict)

        for dirname, subdirlist, filelist in os.walk(rootdir):
            exp = self._get_parent_name(dirname)

            for fname in filelist:
                fpath = os.path.join(dirname, fname)
                run = self._get_parent_name(fpath)

                params = {}

                # Add hyper parameters from directory name (pre-determined convention)
                hyperparams = self._parse_dir(dirname)

                params['hyper'] = hyperparams

                tags = defaultdict(list)
                # Add dependent parameters from tfevent protobuf as key and the most recent value
                for e in tf.train.summary_iterator(fpath):
                    for v in e.summary.value:
                        tags[v.tag].append(v.simple_value)

                params['metric'] = tags
                experiments[exp][run] = params

        return experiments
