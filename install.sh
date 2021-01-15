#!/usr/bin/env bash

python -c "import nltk;nltk.download('framenet_v17')" || exit

rm -rf ODWN_reader
git clone https://github.com/cltl/ODWN_reader
cd ODWN_reader
pip install -r requirements.txt
bash install.sh
cd ..

cd res || exit
rm -rf lemon
mkdir lemon
cd lemon || exit
wget https://lemon-model.net/lemon# -O lemon.ttl || exit
cd ..

rm -rf premon
mkdir premon
cd premon || exit
wget https://knowledgestore.fbk.eu/files/premon/dataset/latest/premon-2018a-fn17-noinf.tql.gz || exit
gunzip premon-2018a-fn17-noinf.tql.gz
cd ../..
python -c 'import rdf_utils;g = rdf_utils.load_nquads_file(path_to_nquad_file="res/premon/premon-2018a-fn17-noinf.tql");rdf_utils.convert_nquads_to_nt(g, output_path="res/premon/premon-2018a-fn17-noinf.nt")' || exit

cd res || exit
rm -rf ontolex
mkdir ontolex
cd ontolex || exit
wget http://www.w3.org/ns/lemon/ontolex -O ontolex.rdf || exit
cd ../..

rm -rf LexicalDataD2TAnnotationTool
git clone https://github.com/cltl/LexicalDataD2TAnnotationTool || exit
cd LexicalDataD2TAnnotationTool || exit
pip install -r requirements.txt
bash install.sh || exit
