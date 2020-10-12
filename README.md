# FrameNet NLTK

The goal of this package is to represent a FrameNet lexicon in the NLTK format
as well as to add new lexical units to it.
You can represent a FrameNet in a different language or
edit an existing FrameNet.

## Prerequisites
Python 3.6 was used to create this project. It might work with older versions of Python.

## Installing
A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

## Resources
The English FrameNet corpus version 1.7 needs to be downloaded. You can use the following command.
```bash
bash install.sh
```

## Usage

Function 1: initialize a new FrameNet lexicon
```python
from FrameNetNLTK import initialize
from nltk.corpus import framenet as fn
initialize(folder='test_lexicon',
           fn_en=fn,
           verbose=2)
```

* **folder**: indicates where the lexicon will be stored on disk. The NLTK convention is to indicate the version in the folder name, e.g., dutch_framenet_v10.
* **fn_en**: result from calling 'from nltk.corpus import framenet as fn'

At the location of **folder**, an empty FrameNet lexicon will be created stripped from all LU information,
but with the frame information intact.

Function 2: load the lexicon
```python
from FrameNetNLTK import load
my_fn = load(folder='test_lexicon',
             verbose=2)
```

You will notice that there is no LU information in the lexicon.
We refer to [the documentation](http://www.nltk.org/howto/framenet.html)
for information about how to use the Python package.

Function 3: add an LU to a lexicalized frame in English FrameNet
We refer to the file [Phenomena](doc/Phenomena.md) for more information about how to represent Lexical Units.


```python
from nltk.corpus import framenet as fn
from FrameNetNLTK import add_lu

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'Californiër'
}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name="Californiër.n",
       lexemes=lexemes,
       definition='van Calfornië',
       status='Created',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       lu_type='singleton',
       incorporated_fe="Origin",
       verbose=2)
```
This will update the lexicon by adding a new LU to the frame **People_by_origin**.
If the lemma and pos combination already exists for the chosen frame in the lexicon, it will not be added.

We can also add LUs consisting of more than one lexeme.
```python 
from nltk.corpus import framenet as fn
from FrameNetNLTK import add_lu

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'senaat',
    'incorporatedFE' : 'Function',
},
{
    'order' : '2',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'I',
    'name' : 's',
},
{
    'order': '3',
    'headword': 'true',
    'breakBefore': 'false',
    'POS': 'N',
    'name': 'verkiezing',
}
]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name="presidentsverkiezing.n",
       lexemes=lexemes,
       definition='het proces van het kiezen van een senator.',
       status='Created',
       pos='N',
       frame='Change_of_leadership',
       provenance='manual',
       lu_type="endocentric compound",
       incorporated_fe="Function",
       verbose=2)
```

Please note that there are five possible values for **lu_type**:
* singleton
* idiom
* phrasal
* endocentric compound
* exocentric compound
 
We highlight that there is an optional lexeme attribute, which is **lu_id**.
In the case of endocentric compounds, as shown above with *presidentsverkiezing*, we
allow the user to link the specific lexemes to the LU that they refer to.
For example, it is possible to first add an LU for "president" and for "verkiezing".
When adding the entire compound "presidentsverkiezing", it is possible
to indicate the LU that each lexeme refers to.
We refer to **test/add_compound_with_lu_id.py** for an example.

Function 4: remove a lexical unit

```python
from FrameNetNLTK import load, remove_lu, get_luid

fn = load('test_lexicon')

lu_id, reason = get_luid(my_fn=fn,
                         frame_label='People_by_origin',
                         lemma='Duitser',
                         pos='N')

remove_lu(your_lexicon_folder='test_lexicon',
          lu_id=lu_id,
          verbose=2)
```
This will remove all information relating to the lexical unit with identifier 1.
You can use the nltk package to find the identiifer of a lexical unit that you want to remove.
What if I want to edit? For now, this is not implemented. The easiest is to remove
the LU and add it with the changes.

Function 5: query the lexicon
```python 
from FrameNetNLTK import load
my_fn = load(folder='test_lexicon')

for lu in my_fn.lus():
    print(lu) 
```

Function 6: optional LU attributes.
The NLTK package is flexible in that it allows to add additional attributes:
```python

from nltk.corpus import framenet as fn
from FrameNetNLTK import add_lu

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'Duitser'
}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name="Duitser.n",
       lexemes=lexemes,
       definition='uit Duitsland',
       status='New',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       lu_type="singleton",
       incorporated_fe="Origin",
       optional_lu_attrs={"RBN_LU_ID" : "r_n-11800", 
                          "Method" : "manual",
                          "FN_EN_LU_ID" : "10547",
                          "RBN_matching_relation" : "equivalence"},
       verbose=2)
```

You will be able to access this information using the syntax **lu.ATTR_NAME**, e.g., *lu.RBN_LU_ID*.
Since this is an open-ended class, there is no validation on what is entered.

Function 7: add a batch of LUs
It is possible to provide a JSON consisting of LUs to be added.

```python
from nltk.corpus import framenet as fn
from FrameNetNLTK import add_lus_from_json

add_lus_from_json(your_lexicon_folder='test_lexicon',
                  fn_en=fn,
                  json_path='res/json/lus.json',
                  verbose=2)
```

Please inspect **res/json/lus.json** for an example.
Please note that the optional attributes must be present in each entry:
* "incorporated_fe" : null or a Frame Element label, e.g., "Origin".
* "timestamp" : null (current date) or a list [YEAR, MONTH, DAY], e.g., [2020, 6, 29]
* "optional_lu_attrs": empty dict or filled with your optional attributes.

Function 8: local http server
It is possible to vizualize your FrameNet similar to how FrameNet visualizes it
([frameIndex](https://framenet.icsi.berkeley.edu/fndrupal/frameIndex) and [luIndex](https://framenet.icsi.berkeley.edu/fndrupal/luIndex)).

```bash 
cd test_lexicon
python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```
Point your browser to the URL shown in the terminal:
* click on **luIndex.xml**
* click on **frameIndex.xml**

Function 9: descriptive statistics
The Python module **stats_utils.py** contains a number of function to compute descriptive statistics.
We highlight the following function:

```python
from FrameNetNLTK import load, get_stats_html

my_fn = load(folder='test_lexicon')
get_stats_html(your_fn=my_fn,
               html_path='descriptive_statistics.html')
```
This will write an html file to disk containing the most important descriptive statistics
about your FrameNet. Feel free to inspect the other functions in stats_utils.py for more functionality.

Function 10: LU RDF URI
We expose a function to generate a RDF URI for an LU

```python
from FrameNetNLTK import load, get_luid, generate_lu_rdf_uri, generate_lexicon_rdf_uri

my_fn = load('test_lexicon')

lu_id, reason = get_luid(my_fn=my_fn,
                         frame_label='Change_of_leadership',
                         lemma='verkiezing',
                         pos='N')

lexicon_uri = generate_lexicon_rdf_uri(namespace='http://rdf.cltl.nl/',
                                             language='nl',
                                             major_version=0,
                                             minor_version=1)
>>>print(lexicon_uri)
http://rdf.cltl.nl/fn_nl-lexicon-0.1


lu_rdf_uri = generate_lu_rdf_uri(your_fn=my_fn,
                                 namespace='http://rdf.cltl.nl/',
                                 language='nl',
                                 major_version=0,
                                 minor_version=1,
                                 lu_id=lu_id)

>>> print(lu_rdf_uri)
http://rdf.cltl.nl/fn_nl-lexicon-0.1-lu-1600860990463
```
The syntax to generate the RDF LU URI is:
* f'{namespace}fn_{language}-lexicon-{major_version}.{minor_version}-lu-{lu_id}'

This means that a URI is generated for a LANGUAGE with MAJOR_VERSION.MINOR_VERSION.

## Documentation
The documentation can be found at **doc/FrameNetNLTK.md**.

## Testing
We make use of pytest for automated testing.
You can test the package by calling:
```bash
cd test
bash all_tests.sh
```

## Authors
* **Marten Postma** (m.c.postma@vu.nl)

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details