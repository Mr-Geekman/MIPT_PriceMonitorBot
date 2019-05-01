"""
Module for checking command line arguments
"""

import os
from data_base_processor import DataBaseProcessor


def is_valid_file(parser, arg):
    """
    Check that arg is file
    :param parser: parser command line arguments
    :param arg: command line argument
    :return: correct argument
    """
    if not os.path.isfile(arg):
        parser.error("The file {} does not exists!".format(arg))
    else:
        return arg


def is_positive_int(parser, arg):
    """
    Check that arg is positive integer
    :param parser: parser command line arguments
    :param arg: command line argument
    :return: correct argument
    """
    if not arg.isdigit() or not int(arg) > 0:
        parser.error("periodicity must be positive integer!")
    else:
        return int(arg)
