# Phenemona
In this document, we describe the phenomena that we
are able to represent in the FrameNetNLTLK format. In the FrameNetNLTK, Lexical Units (LUs) consist of one or more lexemes.
An LU evokes a frame.

## Incorporated Frame Element
In addition to the evoke relationship, the NLTK format also allows to represent
the difference between **ruler.n (LU identifier 1604)** and **rule.v (LU identifier 1603)**.
Both LUs evoke the **Leadership** frame. However, **ruler.n** also has an incorporated Frame Element,
which is **Role**. 

## Enriching the representation of multi-lexeme LUs
Inspired by their productivity in Dutch, we propose to add two attributes at the lexeme level for multi-lexeme LUs:
* **lu_id**: the identifier of the LU that the lexeme refers to.
* **incorporatedFE**: the label of the Frame Element that the lexeme incorporates.
