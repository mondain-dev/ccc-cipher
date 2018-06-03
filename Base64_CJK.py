import sys
import os.path
import getopt
import csv
import random
import base64
import re

### base64 codes
base64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
dBase64Decoding = dict(zip(base64chars, range(len(base64chars))))

N_CodePoints = len(base64chars)*len(base64chars)+len(base64chars) # 64*64+64 = 4160
reBase64Ignore= re.compile(r"[\n\t=]")

### CCC codes
f_CCC_Unicode = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CCC_Unicode.csv'), 'r')
CCC_Unicode  = list(csv.reader(f_CCC_Unicode))
dCCCDecoding = dict(zip([e[0] for e in CCC_Unicode], [e[2].decode('utf-8') for e in CCC_Unicode]))
dCCCEncoding = dict()
for e in CCC_Unicode :
  for c in e[2].split():
    dCCCEncoding[c.decode('utf-8')] = e[0]

### Radical Codes for ~5% of codepoints unmapped in CCC
f_RadicalCount = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'RadicalCountTable.csv'), 'r')
RadicalCount  = list(csv.reader(f_RadicalCount))
dRadicalCountEncoding = [e[1].decode('utf-8') for e in RadicalCount]
dRadicalCountDecoding = dict()
for e in RadicalCount :
    for c in e[1].decode('utf-8'):
        dRadicalCountDecoding[c] = int(e[0])

def read_char(file_object):
    for line in file_object:
        for char in line.decode('utf-8'):
            yield char

def Base64ToCodePoint(str_base64):
    plaintext = reBase64Ignore.sub('', str_base64)
    list_codepoint = []
    for c1,c2 in zip(plaintext[0::2], plaintext[1::2]):
        assert c1 in base64chars and c2 in base64chars
        n1 = dBase64Decoding[c1]
        n2 = dBase64Decoding[c2]
        list_codepoint.append(n1*64 + n2)
    if len(plaintext) % 2:
        c=plaintext[-1:]
        assert c in base64chars
        n=dBase64Decoding[c]
        list_codepoint.append(64*64 + n)
    return list_codepoint

def CodePointToCJK(list_codepoint):
    str_CJK = ''
    for n in list_codepoint:
        if '%04d' % n in dCCCDecoding:
            # CCC
            str_CJK += random.choice(dCCCDecoding['%04d' % n].split())
        elif '%04d' % (n + N_CodePoints) in dCCCDecoding:
            str_CJK += random.choice(dCCCDecoding['%04d' % (n + N_CodePoints)].split())
        elif '%04d' % (n + 2*N_CodePoints) in dCCCDecoding:
            str_CJK += random.choice(dCCCDecoding['%04d' % (n + 2*N_CodePoints)].split())
        else:
            str_CJK += (random.choice(dRadicalCountEncoding[n/100]) + random.choice(dRadicalCountEncoding[n%100]))
    return str_CJK

def CJKToCodePoint(str_CJK):
    list_codepoint = []
    x = iter(str_CJK)
    for c in x:
        if c in dCCCEncoding:
            list_codepoint.append(int(dCCCEncoding[c]) % N_CodePoints)
        elif c in dRadicalCountDecoding:
            n = dRadicalCountDecoding[c]
            c1 = next(x, None)
            if c1:
                if c1 in dRadicalCountDecoding:
                    n = n*100 + dRadicalCountDecoding[c1]
                    list_codepoint.append(n)
                elif c1 in dCCCEncoding:
                    list_codepoint.append(n)
                    list_codepoint.append(int(dCCCEncoding[c1]))
                else:
                    list_codepoint.append(n)
            else:
                list_codepoint.append(n)
    return list_codepoint

def CJKToBase64(str_CJK):
    str_base64 = ''
    for n in CJKToCodePoint(str_CJK):
        if n > 0:
            if n < 64*64:
                n1 = n/64
                n2 = n%64
                str_base64 += (base64chars[n1] + base64chars[n2])
            elif n - 64*64 < 64:
                str_base64 += base64chars[n - 64*64]
    return str_base64

def Base64CJKEncoder(input_base64):
  for c in input_base64:
      c = reBase64Ignore.sub('', c)
      if c and c in base64chars:
            n = dBase64Decoding[c]
            c1 = next(input_base64, None)
            if not c1 is None:
                c1 = reBase64Ignore.sub('', c1)
            while c1 == '':
                c1 = next(input_base64, None)
                if not c1 is None:
                    c1 = reBase64Ignore.sub('', c1)
            if c1:
                yield CodePointToCJK(Base64ToCodePoint(c+c1))
            else:
                yield CodePointToCJK(Base64ToCodePoint(c))

def Base64CJKDecoder(input_cjk):
    for C in input_cjk:
        if C in dRadicalCountDecoding:
            C1 = next(input_cjk, None)
            while C1:
                if C1 in dRadicalCountDecoding:
                    C += C1
                    yield CJKToBase64(C)
                    break
                else:
                    C1 = next(input_cjk, None)
            if not C1:
                yield CJKToBase64(C)
        else:
            yield CJKToBase64(C)

def main():
    in_file  = None
    out_file = None
    encoding = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:edh", ["in=", "out=",'encode','decode','help'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        helpBase64CJK()
        sys.exit(2)
    for o, a in opts:
        if o in ("-i", "--in"):
            in_file = a
        elif o in ("-o", "--out"):
            out_file = a
        elif o in ("-d", "--decode"):
            encoding = False
        elif o in ("-e", "--encode"):
            encoding = True
        elif o in ("-h", "--help"):
            helpBase64GB()
            sys.exit()
        else:
            assert False, "unhandled option"

    if not in_file:
        helpBase64CJK()
        sys.exit(1)

    out_writer = sys.stdout
    if out_file:
        out_writer = open(out_file, "w")

    line_len_counter=0
    if encoding:
        MAX_LINE_LEN=16
        line_len_counter=0
        f = open(in_file, 'r')
        for C in Base64CJKEncoder(read_char(f)):
            for s in C:
                out_writer.write(s.encode('utf8'))
                line_len_counter+=1
                if line_len_counter >= MAX_LINE_LEN:
                    out_writer.write('\n')
                    line_len_counter=0
        if line_len_counter > 0:
            out_writer.write('\n')
    else:
        f = open(in_file, 'r')
        base64_counter=0
        for C in Base64CJKDecoder(read_char(f)):
            for s in C:
                base64_counter+=1
                out_writer.write(s)
        if base64_counter % 3:
            for _ in range(3-(base64_counter % 3)):
                out_writer.write("=")

def helpBase64CJK():
    args = sys.argv[0:]
    print(''.join(['Usage: \n', args[0], ' [OPTIONS]']))
    print('  OPTIONS:')
    print('  -i, --in=:       input file (required)')
    print('  -o, --out=:      output file')
    print('  -e, --encoding:  encode the input')
    print('  -d, --decoding:  decode the input')
    print('  -h, --help:      print this help')

if __name__ == "__main__":
    main()
