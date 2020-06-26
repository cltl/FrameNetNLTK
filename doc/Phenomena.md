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
* **evokes**: true or false, indicates whether this specific lexeme evokes the frame instead of the entire LU.
* **incorporatedFE**: the label of the Frame Element that the lexeme incorporates.

### Examples
* **presidentsverkiezing "presidential election"**: evokes Change_of_leadership. The lexeme *verkiezing* evokes the frame and *president* incorporates the Frame Element *Function*:
    * president "president" (evokes="false", incorporatedFE="Function")
    * s "bound morpheme" ("evokes"="false")
    * verkiezing "election" (evokes="true")
* **aanslagpleger "attack committer"**: This can either by interpreted as *pleger* "committer" evoking a frame and *aanslag* "aanslag" serving as a Frame Element, or that *aanslag* "aanslag" evokes  a frame and *pleger* "committer" serves as a Frame Element. We propose to represent these phenomena in the following manner:
    * aanslag "attack" (evokes="true")
    * pleger "committer" (evokes="false", incorporatedFE="Assailant")
