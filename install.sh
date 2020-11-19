#!/usr/bin/env bash

python -c "import nltk;nltk.download('framenet_v17')"

cd res/rdf
rm -rf lemon.ttl
wget https://lemon-model.net/lemon# -O lemon.ttl
cd ..

rm -rf premon
mkdir premon
cd premon
wget https://knowledgestore.fbk.eu/files/premon/dataset/latest/premon-2018a-fn17-noinf.tql.gz
gunzip premon-2018a-fn17-noinf.tql.gz
cd ../..
python -c 'import rdf_utils;g = rdf_utils.load_nquads_file(path_to_nquad_file="res/premon/premon-2018a-fn17-noinf.tql");rdf_utils.convert_nquads_to_nt(g, output_path="res/premon/premon-2018a-fn17-noinf.nt")'
