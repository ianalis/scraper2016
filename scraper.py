#!/usr/bin/env python

###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2016, Christian Alis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import json
import os
import random
import time
import glob
import argparse
import cfscrape
from urlparse import urljoin

__author__ = "Christian Alis"
__email__ = "ianalis [at] gmail.com"
__license__ = "MIT"

BASE_URL = 'https://www.pilipinaselectionresults2016.com'

_ = lambda s: s.replace('/', '_')

def download_json(scraper, target_info, parent_dirs, basedir, 
                  delay_min, delay_max):
    """Download json file, save it then return json content"""
    name = _(target_info['name'])
    suburl = target_info['url']
    out_dir = os.path.join(basedir, *parent_dirs)
    out_fpath = os.path.join(out_dir, name+'.json')
    
    print('Attempting to process/download: %s' % out_fpath)
        
    # download file only if it doesn't exist
    if os.path.exists(out_fpath):
        return json.load(open(out_fpath))
    else:
        # wait between delay_min and delay_max
        time.sleep(random.uniform(delay_min, delay_max))
                   
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        content = scraper.get(urljoin(BASE_URL, suburl))\
                         .content
        out_file = open(out_fpath, 'w')
        out_file.write(content)
        out_file.close()
        return json.loads(content)

def scrape_results(basedir='data', region=None, delay_min=1, delay_max=3):
    scraper = cfscrape.create_scraper()
    parent_dirs = []
    root_info = {'name': 'PHILIPPINES',
                 'url': 'data/regions/root.json'}
    root = download_json(scraper, root_info, parent_dirs, basedir, 
                         delay_min, delay_max)
    parent_dirs.append('PHILIPPINES')
    
    if region is None:
        regions = root['subRegions'].values()
    else:
        regions = [root['subRegions'][region]]
    
    for reg in regions:
        region_content = download_json(scraper, reg, parent_dirs,
                                       basedir, delay_min, delay_max)
        parent_dirs.append(_(region_content['name']))
        
        for province in region_content['subRegions'].values():
            province_content = download_json(scraper, province, parent_dirs,
                                             basedir, delay_min, 
                                             delay_max)
            parent_dirs.append(_(province_content['name']))
            
            for mun in province_content['subRegions'].values():
                mun_content = download_json(scraper, mun, parent_dirs,
                                            basedir, delay_min, 
                                            delay_max)
                parent_dirs.append(_(mun_content['name']))
                
                for brgy in mun_content['subRegions'].values():
                    brgy_content = download_json(scraper, brgy, parent_dirs,
                                                 basedir, delay_min, 
                                                 delay_max)
                    parent_dirs.append(_(brgy_content['name']))
                    
                    for precinct in brgy_content['subRegions'].values():
                        precinct_content = download_json(scraper, precinct, 
                                                         parent_dirs,
                                                         basedir, 
                                                         delay_min, delay_max)
                        parent_dirs.append(_(precinct_content['name']))
                        
                        # since we can't know the name of each position
                        # (contest) hence the filenames until we download the
                        # contest json, we assume all contests were downloaded
                        # already if the number of json files in the precinct
                        # matches the number of contests in the list
                        precinct_dir = os.path.join(basedir, *parent_dirs)
                        json_list = glob.glob(os.path.join(precinct_dir, 
                                                           '*.json'))
                        try:
                            if len(json_list) != \
                               len(precinct_content['contests']):
                                for contest in precinct_content['contests']:
                                    # remove delay at contests level because a 
                                    # browser would download these files
                                    # simultaneously anyway
                                    content = scraper.get(urljoin(BASE_URL, 
                                                               contest['url']))\
                                                     .content
                                    contest_content = json.loads(content)
                                    out_dir = os.path.join(basedir, 
                                                        *parent_dirs)
                                    if not os.path.exists(out_dir):
                                        os.makedirs(out_dir)
                                    out_fpath = os.path.join(out_dir, 
                                                contest_content['name']+'.json')
                                    out_file = open(out_fpath, 'w')
                                    out_file.write(content)
                                    out_file.close()
                        except ValueError:
                            # precinct hasn't transmitted yet
                            print('FAILED: %s' % precinct_dir)
                            
                        parent_dirs.pop()
                        
                    parent_dirs.pop()
                            
                parent_dirs.pop()
                            
            parent_dirs.pop()
                            
        parent_dirs.pop()
                            
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape data from '
                                             'pilipinaselectionresults2016.com')
    parser.add_argument('--basedir', '-b', default='data',
                        help='directory where to store data (default: data)')
    parser.add_argument('--region', '-r', 
                        help='region from where scrape data')
    parser.add_argument('--delay_min', type=float, default=1,
                        help='minimum delay between downloads, in seconds '
                             '(default: 1)')
    parser.add_argument('--delay_max', type=float, default=3,
                        help='maximum delay between downloads, in seconds '
                             '(default: 3)')

    args = parser.parse_args()
    scrape_results(**vars(args))