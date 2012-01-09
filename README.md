Balie Commandline Interface
===========================

`balie-ner-cli` provides a commandline interface to the named-entity
recognition features of [Balie](http://balie.sourceforge.net/
 "baseline information extraction") — a Java library that can be used
to perform various NLP tasks.  


INSTALLATION
============

Download and install Balie if you haven't done so. Switch back to the
`balie-ner-cli` directory. Edit the `balie_dir` variable in `config.yml` to
point to your Balie installation directory.


USAGE
=====

`python balie-cli.py -i input.txt` will read text from *input.txt* and print a
list of named entities to STDOUT (one NE per line).

`python balie-cli.py -i input.txt -o output.txt` will read text from
*input.txt* and write a list of named entities to *output.txt* (one NE per
line).

Example
-------

    $ cat input.txt 
    Barack Obama, Hillary Clinton and George Bush met in a bar in Wisconsin. They
    were discussing issues regarding the Netherlands, the Queen of England and
    Boy George.

    $ python ./balie-cli.py -i input.txt
    ('Hillary Clinton', 'PERSON')
    ('George Bush', 'PERSON')
    ('Wisconsin', 'LOCATION')
    ('Queen', 'PERSON')
    ('England', 'LOCATION')
    ('Boy George', 'PERSON')

Note that *Barack Obama* wasn't recognized, as the training data that Balie
comes with is already a few years old (ca. 2007).


LICENCE
=======

GPL 2 or later.

CONTACT
=======

Arne Neumann <neumann.arne@gmail.com>



