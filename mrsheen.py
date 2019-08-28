import os
import json
import argparse
import logging
import datetime
import shutil
import sys
import six
from colorlog import ColoredFormatter


def _setup_logging(verbosity):
        """
        Setup logging with desired verbosity
        :param verbosity:
        :return:
        """
        logging.getLogger("dirtools").setLevel(logging.WARNING)

        logger = logging.getLogger()
        LOGFORMAT = '%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(name)-12s %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
        LOGCOLOUR = {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
        formatter = ColoredFormatter(LOGFORMAT, log_colors=LOGCOLOUR)
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        logger.addHandler(stream)

        logger.setLevel((logging.ERROR - (verbosity * 10)))
        return logger


def sheen_walk(basedir, subs, base_clean,logger,reverse):
    for dirpath,dirnames, filenames in os.walk(basedir):

        for file in filenames:
            newpath = base_clean+"/"+string_replace(dirpath,subs,reverse)
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            cleanpath = os.path.join(newpath, string_replace(file,subs,reverse))
            inputpath = os.path.join(dirpath, file)

            # do the replacement line-by-line
            with open(inputpath) as infile, open(cleanpath, 'w') as outfile:
                logger.debug("Processing file %s" % infile.name)
                line_number = 0
                process_cert = False
                for line in infile:
                    line_number += 1
                    # check if this is the start of a certificate
                    if "BEGIN" in line:
                        if "END" in line:
                            continue
                        else:
                            outfile.write(line)
                            process_cert = True
                            continue
                    elif process_cert:
                        if "END" not in line:
                            continue
                        else:
                            outfile.write(line)
                            process_cert = False
                    else:
                        try:
                            outfile.write(string_replace(line,subs,reverse))
                        except UnicodeDecodeError:
                            logger.error("Error processing line %d in file %s" % (line_number,infile.name))
                logger.debug("Cleaned file written to %s" % outfile.name)
            infile.close()
            outfile.close()


def cleanup_git(basedir):
    for dirpath, dirnames, filenames in os.walk(basedir):
        if ".git" in dirpath:
            shutil.rmtree(dirpath)


def string_replace(input,subs,reverse):
    with open(subs) as json_file:
        json_data = json.load(json_file)
        for k,v in six.iteritems(json_data):
            if(reverse):
                input = input.replace(v,k)
            else:
                input = input.replace(k,v)
    return input


def main():
    parser = argparse.ArgumentParser(description='Replace occurrences of specific patterns in files and folders')

    parser.add_argument('--dir', dest='basedir', help='Base export directory')
    parser.add_argument('--json-replace', dest='subs', help='JSON file with key-value pairs of replacements to make')
    parser.add_argument('--reverse',dest='reverse', action="store_true", help='Reverse the order of the substitutions')

    parser.add_argument("-v", "--verbose", action="count", dest="verbosity",
                        help="Verbose mode. Can be used multiple times to increase output. Use -vvv for debugging output.")
    args = parser.parse_args()

    # Setup logging
    verbosity = args.verbosity
    if args.verbosity == None or args.verbosity < 0:
        verbosity = 0
    logger = _setup_logging(verbosity)

    if not args.basedir:
        logger.error("Base directory not specified")
        parser.print_help()
        sys.exit(1)
    elif not args.subs:
        logger.error("JSON substitutions file not specified")
        parser.print_help()
        sys.exit(1)

    # Create the cleaned directory structure, replacing dirnames with substitutions
    base_clean = args.basedir + "_mrsheen_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logger.info("Base cleaned directory is " + base_clean)
    # cleanup any git subdirectories
    logger.info("Starting git deletion")
    cleanup_git(basedir=args.basedir)
    logger.info("Starting directory walk")
    sheen_walk(basedir=args.basedir, subs=args.subs, base_clean=base_clean,logger=logger, reverse=args.reverse)

if __name__ == "__main__":
    main()
