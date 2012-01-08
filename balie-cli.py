# -*- coding: utf-8 -*-
# Author: Arne Neumann <neumann.arne@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import sys
import re
import yaml
import argparse
from subprocess import Popen, PIPE

CONFIG_FILE = "config.yml"
settings = yaml.load( open(CONFIG_FILE, "r") )

TEST_SENTENCES = """
Barack Obama, Hillary Clinton and George Bush met in a bar in Wisconsin. They
were discussing issues regarding the Netherlands, the Queen of England and
Boy George.
"""


def balie_ner_chunker(untagged):
    """
    uses external tool Balie to find named entities.

    @param untagged: untagged and untokenized sentence(s)
    @type untagged: C{str}

    @return: a list of (named entity, entity type) tuples
    @rtype: C{list} of C{tuple}s of (C{str}, C{str})
    """
    working_dir = os.getcwd()
    balie_dir = settings["balie_dir"]
    balie_source = "RTESentence.java"

    __generate_balie_code(untagged, balie_dir, balie_source)
    __compile_balie_code(balie_dir, balie_source)

    balie_class_name, extension = os.path.splitext(balie_source)
    balie = Popen(["java", "-cp", ".:./lib/weka.jar", balie_class_name],
                  cwd=balie_dir, shell=False, stdout=PIPE, stderr=PIPE)
    #~ if balie.stderr.read():
        #~ print balie.stderr
        #~ raise Exception("Java Runtime Error")

    balie_regex = re.compile('<ENAMEX\s+[^>]*?TYPE="(?P<type>\w+)"\s+[^>]*?ALIAS="(?P<alias>\w+)">(?P<entity>.+?)</ENAMEX>', re.DOTALL | re.I)
    output = balie.stdout.read()
    named_entities = [(ne, ne_type) for (ne_type, pos, ne) in balie_regex.findall(output)]
    os.chdir(working_dir)
    return named_entities


def __generate_balie_code(untagged_text, balie_dir, balie_file_name):
    """
    Balie is a Java library without a commandline interface. That's why
    we'll generate some boilerplate code in Java that uses Balie as a
    library and stores it in 'balie_file'.
    """
    header = '''
    /* original author: David Nadeau (pythonner@gmail.com)
       original licence: GPL 2 or later
       adaptation: Arne Neumann (neumann.arne@gmail.com) */

    import ca.uottawa.balie.Balie;
    import ca.uottawa.balie.DisambiguationRulesNerf;
    import ca.uottawa.balie.LexiconOnDisk;
    import ca.uottawa.balie.LexiconOnDiskI;
    import ca.uottawa.balie.NamedEntityRecognitionNerf;
    import ca.uottawa.balie.NamedEntityTypeEnumMappingNerf;
    import ca.uottawa.balie.PriorCorrectionNerf;
    import ca.uottawa.balie.TokenList;
    import ca.uottawa.balie.Tokenizer;

    public class RTESentence {

        public static void Test() {
            String strText = '''

    footer = ''' " ";

                Tokenizer tokenizer = new Tokenizer(Balie.LANGUAGE_ENGLISH, true);

                LexiconOnDiskI lexicon = new LexiconOnDisk(LexiconOnDisk.Lexicon.OPEN_SOURCE_LEXICON);
                DisambiguationRulesNerf disambiguationRules = DisambiguationRulesNerf.Load();

                tokenizer.Reset();
                tokenizer.Tokenize(strText);
                TokenList alTokenList = tokenizer.GetTokenList();

                NamedEntityRecognitionNerf ner = new NamedEntityRecognitionNerf(
                        alTokenList,
                        lexicon,
                        disambiguationRules,
                        new PriorCorrectionNerf(),
                        NamedEntityTypeEnumMappingNerf.values(),
                        false);
                ner.RecognizeEntities();

                alTokenList = ner.GetTokenList();

                String strAnnotated = alTokenList.TokenRangeText(0, alTokenList.Size(), false, true, true, true, false, true);

                System.out.println(strAnnotated);
        }

        public static void main(String[] args) {
            Test();
        }

    }
    '''
    content = ""
    for line in untagged_text.splitlines():
        line_rstripped = line.rstrip(os.linesep)
        line_escaped = line_rstripped.replace('"', '\\"')
        # double quotes need to be escaped as Java doesn't have multi-line
        # strings
        content += '"{0} " +\n'.format(line_escaped)

    os.chdir(balie_dir)
    output_file = open(balie_file_name, "w")
    output_file.writelines([header, content, footer])
    output_file.close()


def __compile_balie_code(balie_dir, balie_file_name):
    javac = Popen(["javac", balie_file_name], shell=False, cwd=balie_dir,
                  stdout=PIPE, stderr=PIPE)
    javac.stderr.read()
    if javac.stderr.read():
        raise Exception("javac compile error")

def parse_cli_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", type=str,
        help="Path to input file.")
    parser.add_argument("-o", "--output", type=str,
        help="Path to output file. Writes to STDOUT if no file is given.")

    args = parser.parse_args(argv)

    if args.input is not None:
        try:
            input_file = open(args.input, "r")
            input_str = input_file.read()
        except IOError:
            print "Can't read from input file: {0}".format(args.input)
            sys.exit(1)
    else:
        print "No input file given."
        sys.exit(1)

    if args.output is not None:
        output_file = open(args.output, "w")
    else:
        output_file = sys.stdout

    return input_str, output_file


if __name__ == "__main__":
    input_str, output_file = parse_cli_args(sys.argv[1:])
    named_entities = balie_ner_chunker(input_str)
    for named_entity in named_entities:
        output_file.write("{0}\n".format(named_entity))
    output_file.close()

