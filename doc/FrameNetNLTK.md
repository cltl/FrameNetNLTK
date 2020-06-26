# FrameNet in NLTK format

## XML representation
Information about each LU is stored in three files:
* luIndex/lu
* frame/FRAME_NAME.xml which the LU evokes
* lu/LU_ID.xml a single file with a description of the LU

## Validation steps

### Status
FrameNet provides each LU with a status.
The available set can be found at **../validation_utils.STATUS**.
We refer to FrameNet for the documentation about the definitions of the status.

### POS
Each LU is provided with a part of speech tag.
The available set can be foudn at **../validation_utils.POS**.
We refer to FrameNet for the documentation about the definitions of the part of speech tags.

We've added one part of speech tag:
* **I** for infix, which we use for bound morphemes in compounds.

### Lexemes
Each LU contains one or more lexemes, for which FrameNet defines the following attributes:
* order: the orthographic order as a string, e.g., '1' or '2'
* headword: the lexeme is the grammatical head as a string: "true" or "false"
* breakBefore: a space before the lexeme, e.g., "true" or "false". In the case of "give up", breakBefore would be "yes" for the lexeme "up".
* POS: see header POS
* name: the lemma of the LU without the POS, e.g., "surrender" 

If an LU consists of only one lexeme, 'headword' is false.