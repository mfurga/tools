#!/usr/bin/env python2

import argparse
import sys

# Parse command line arguments
parser = argparse.ArgumentParser('./LEB128',
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100, width=150))
parser.add_argument('number', type=int, help='Specify number')
parser.add_argument('-e', '--encode', action='store_true', default=False, help='Encode unsigned number')
parser.add_argument('-d', '--decode', action='store_true', default=False, help='Decode unsigned number')
args = parser.parse_args()


# Encode unsigned integer
def leb128_encode(number):
    chunks = []
    n = 0

    while number:
        byte = number & 0x7f
        number >>= 7

        if number:
            byte |= 0x80

        chunks.append(byte)

    for i in chunks:
        n <<= 8
        n |= i

    return n


# Decode unsigned integer
def leb128_decode(number):
    chunks = []
    n = 0

    size = len(bin(number)[2:])
    shift = size - 8

    byte = (number >> shift) & 0xff
    high = byte >> 7

    chunks.append(byte & 0x7f)

    while high:
        shift -= 8
        byte = (number >> shift) & 0xff
        chunks.append(byte & 0x7f)
        high = byte >> 7

    for i in chunks[::-1]:
        n <<= 7
        n |= i

    return n


if args.decode:
    print leb128_decode(args.number)
else:
    print leb128_encode(args.number)
