#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, S. <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
__author__ = 'essepuntato'

import argparse
import os
import shutil
import logging
from rdflib import Graph

# Formats available
formats = {
    "json-ld": "json",
    "xml": "rdf",
    "turtle": "ttl"
}


def load(rdf_file_path, tmp_dir=None):
    if os.path.isfile(rdf_file_path):
        try:
            cur_graph = __load_graph(rdf_file_path)
            return cur_graph
        except IOError:
            if tmp_dir is not None:
                current_file_path = tmp_dir + os.sep + "tmp_rdf_file.rdf"
                shutil.copyfile(rdf_file_path, current_file_path)
                try:
                    cur_graph = __load_graph(current_file_path)
                    return cur_graph
                except IOError as e:
                    log.error("It was impossible to handle the format used for "
                              "storing the file (stored in the temporary path) '%s'. "
                              "Additional details: %s" % (current_file_path, str(e)))
                os.remove(current_file_path)
            else:
                log.error("It was impossible to try to load the file from the "
                          "temporary path '%s' since that has not been specified in "
                          "advance" % rdf_file_path)
    else:
        log.error("The file specified ('%s') doesn't exist." % rdf_file_path)


def __load_graph(file_path):
    errors = ""

    current_graph = Graph()

    for cur_format in formats:
        try:
            current_graph.parse(file_path, format=cur_format)
            return current_graph
        except Exception as e:
            errors = " | " + str(e)  # Try another format

    raise IOError("1", "It was impossible to handle the format used for storing the file '%s'%s" %
                  (file_path, errors))


def store(dest_dir, file_name, f):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    dest_file = dest_dir + os.sep + file_name
    g.serialize(dest_file, format=f)
    log.info("RDF graph serialised in %s format and stored in %s" % (f, dest_file))


# Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("gerfo.py - generate RDF formats in Python")
    arg_parser.add_argument("-s", "--src", dest="source_file", required=True,
                            help="The source RDF file.")
    arg_parser.add_argument("-d", "--dst", dest="dest_dir", required=True,
                            help="The directory where to store all the converted data.")
    arg_parser.add_argument("-v", "--ver", dest="version_dir",
                            help="The directory where to store the current version of the RDF file.")
    arg_parser.add_argument("-t", "--tmp", dest="tmp_dir",
                            help="A temporary directory that will be used in case there will be "
                                 "issues in loading RDF graphs from files which have a path "
                                 "with special characters (which is a bug introduced by RDFLIB).")
    args = arg_parser.parse_args()

    # Set logger
    log = logging.getLogger("GeRFo logger")
    log_h = logging.StreamHandler()
    log_f = logging.Formatter('%(levelname)s - %(message)s')
    log_h.setFormatter(log_f)
    log.addHandler(log_h)
    log.setLevel(logging.INFO)

    g = load(args.source_file, args.tmp_dir)
    if g is not None:
        cur_name = os.path.splitext(os.path.basename(args.source_file))[0]
        for f in formats:
            store(args.dest_dir, cur_name + "." + formats[f], f)
            if args.version_dir is not None:
                store(args.version_dir, cur_name + "." + formats[f], f)