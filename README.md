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

Step 1: initialize a new FrameNet lexicon
```python
from FrameNLTK import initialize
from nltk.corpus import framenet as fn
initialize(folder='test_lexicon',
           fn_en=fn,
           verbose=2)

```

* **folder**: indicates where the lexicon will be stored on disk. The NLTK convention is to indicate the version in the folder name, e.g., dutch_framenet_v10.
* **fn_en**: result from calling 'from nltk.corpus import framenet as fn'

At the location of **folder**, an empty FrameNet lexicon will be created stripped from all LU information,
but with the frame information intact.

Step 2: load the lexicon
```python
from FrameNetNLTK import load
my_fn = load(folder='test_lexicon')
```

You will notice that there is no LU information in the lexicon.
We refer to [the documentation](http://www.nltk.org/howto/framenet.html)
for information about how to use the Python package.

Step 3: add an LU to a lexicalized frame in English FrameNet
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
       lexemes=lexemes,
       definition='van Calfornië',
       status='New',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       incorporated_fe="Origin",
       verbose=2)
```
This will update the lexicon by adding a new LU to the frame **People_by_origin**.
If the lemma and pos combination already exists for the chosen frame in the lexicon, it will not be added.

We can also add LUs consisting of more than one lexeme:
```python 
from nltk.corpus import framenet as fn
from FrameNetNLTK import add_lu

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'president',
    'evokes' : 'false',
    'incorporatedFE' : 'Function'
},
{
    'order' : '2',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'I',
    'name' : 's',
    'evokes' : 'false'
},
{
    'order': '3',
    'headword': 'true',
    'breakBefore': 'false',
    'POS': 'N',
    'name': 'verkiezing',
    'evokes' : 'true'
}
]
add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='het proces van het kiezen van een president.',
       status='New',
       pos='N',
       frame='Change_of_leadership',
       provenance='manual',
       incorporated_fe="Function",
       verbose=2)
```

Step 4: remove a lexical unit

```python
from FrameNetNLTK import remove_lu

remove_lu(your_lexicon_folder='test_lexicon',
          lu_id=1)
```
This will remove all information relating to the lexical unit with identifier 1.
You can use the nltk package to find the identiifer of a lexical unit that you want to remove.
What if I want to edit? For now, this is not implemented. The easiest is to remove
the LU and add it with the changes.

Step 5: query the lexicon
```python 
from FrameNetNLTK import load
my_fn = load(folder='test_lexicon')

for lu in my_fn.lus():
    print(lu) 
```

Step 6: optional LU attributes.
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
       lexemes=lexemes,
       definition='uit Duitsland',
       status='New',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       incorporated_fe="Origin",
       optional_lu_attrs={"RBN_LU_ID" : "r_n-11800", "relation" : "equivalence"},
       verbose=2)
```

You will be able to access this information using the syntax **lu.ATTR_NAME**, e.g., *lu.RBN_LU_ID*.
Since this is an open-ended class, there is no validation on what is entered.

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