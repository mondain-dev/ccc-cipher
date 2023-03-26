import sys
import os.path
import getopt
import csv
import random
import re

### base32 codes
base32chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
B = len(base32chars) # i.e. 32
dictBase32Decoding = dict(zip(base32chars, range(len(base32chars))))

NCodePoints = B * B + B # 32*32+32 = 1056
reBase32Ignore= re.compile(r"[\n\t=]")

### CCC codes
fCCCUnicode = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CCC_Unicode.csv'), 'r')
CCCUnicode  = list(csv.reader(fCCCUnicode))
dictCCCDecoding = dict(zip([e[0] for e in CCCUnicode], [e[2].decode('utf-8') for e in CCCUnicode]))
dictCCCEncoding = dict()
for e in CCCUnicode :
  for c in e[2].split():
    dictCCCEncoding[c.decode('utf-8')] = e[0]


def read_char(file_object):
    for line in file_object:
        for char in line.decode('utf-8'):
            yield char

def Base32ToCodePoint(strBase32):
    plaintext = reBase32Ignore.sub('', strBase32)
    listCodePoints = []
    for c1,c2 in zip(plaintext[0::2], plaintext[1::2]):
        assert c1 in base32chars and c2 in base32chars
        n1 = dictBase32Decoding[c1]
        n2 = dictBase32Decoding[c2]
        listCodePoints.append(n1 * B + n2)
    if len(plaintext) % 2:
        c=plaintext[-1:]
        assert c in base32chars
        n=dictBase32Decoding[c]
        listCodePoints.append(B * B + n)
    return listCodePoints

def CodePointToCJK(listCodePoints):
    strCJK = ''
    for n in listCodePoints:
        for k in range(len(dictCCCDecoding) // NCodePoints + 1):
            codepoint = '%04d' % (n + NCodePoints*k)
            if codepoint in dictCCCDecoding:
                # CCC
                strCJK += random.choice(dictCCCDecoding[codepoint].split())
                break
    return strCJK

def CJKToCodePoint(strCJK):
    listCodePoint = []
    x = iter(strCJK)
    for c in x:
        if c in dictCCCEncoding:
            listCodePoint.append(int(dictCCCEncoding[c]) % NCodePoints)
    return listCodePoint

def CJKToBase32(strCJK):
    strBase32 = ''
    for n in CJKToCodePoint(strCJK):
        if n >= 0:
            if n < B*B:
                n1 = n / B
                n2 = n % B
                strBase32 += (base32chars[n1] + base32chars[n2])
            elif n - B*B < B:
                strBase32 += base32chars[n - B*B]
    return strBase32

def Base32CJKEncoder(inputBase32):
  for c in inputBase32:
      c = reBase32Ignore.sub('', c)
      if c and c in base32chars:
            n = dictBase32Decoding[c]
            c1 = next(inputBase32, None)
            if not c1 is None:
                c1 = reBase32Ignore.sub('', c1)
            while c1 == '':
                c1 = next(inputBase32, None)
                if not c1 is None:
                    c1 = reBase32Ignore.sub('', c1)
            if c1:
                yield CodePointToCJK(Base32ToCodePoint(c+c1))
            else:
                yield CodePointToCJK(Base32ToCodePoint(c))

def Base32CJKDecoder(inputCJK):
    for C in inputCJK:
        yield CJKToBase32(C)

# assert all([len(CodePointToCJK([i])) > 0 for i in range(NCodePoints)])

def main():
    in_file  = None
    out_file = None
    encoding = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:edh", ["in=", "out=",'encode','decode','help'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        helpBase32CJK()
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
            helpBase32CJK()
            sys.exit()
        else:
            assert False, "unhandled option"

    # if not in_file:
    #     helpBase32CJK()
    #     sys.exit(1)

    out_writer = sys.stdout
    if out_file:
        out_writer = open(out_file, "w")

    line_len_counter=0
    if encoding:
        MAX_LINE_LEN=16
        line_len_counter=0
        f = sys.stdin
        if in_file:
            f = open(in_file, 'r')
        for C in Base32CJKEncoder(read_char(f)):
            for s in C:
                out_writer.write(s.encode('utf8'))
                line_len_counter+=1
                if line_len_counter >= MAX_LINE_LEN:
                    out_writer.write('\n')
                    line_len_counter=0
        if line_len_counter > 0:
            out_writer.write('\n')
    else:
        f = sys.stdin
        if in_file:
            f = open(in_file, 'r')
        base32Counter=0
        for C in Base32CJKDecoder(read_char(f)):
            for s in C:
                base32Counter+=1
                out_writer.write(s)
        if base32Counter % 8 == 2:
            out_writer.write("======")
        elif base32Counter % 8 == 4:
            out_writer.write("====")
        elif base32Counter % 8 == 5:
            out_writer.write("===")
        elif base32Counter % 8 == 7:
            out_writer.write("=")
        if base32Counter > 0:
            out_writer.write('\n')

def helpBase32CJK():
    args = sys.argv[0:]
    print(''.join(['Usage: \n', args[0], ' [OPTIONS]']))
    print('  OPTIONS:')
    print('  -i, --in=:       input file, use stdin if not supplied')
    print('  -o, --out=:      output file')
    print('  -e, --encoding:  encode the input')
    print('  -d, --decoding:  decode the input')
    print('  -h, --help:      print this help')

if __name__ == "__main__":
    main()
