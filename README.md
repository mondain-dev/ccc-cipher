# CCC Cipher
A `base32` ⇌ CJK cipher using the [Chinese Commercial Code](https://en.wikipedia.org/wiki/Chinese_telegraph_code) (CCC), aka the Chinese Telegraph Code.

## Usage
There are two components in this cipher:
* `Base32CJK.py` encodes base32 strings into CJK strings, and decodes the original base32 from CJK codes. Note that the encoding does not work for base64.
* Entryption-Decryption scripts
  * `cipher.sh` encrypts any file (binary or otherwise) using [AES-256](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) with [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) implemented in `openssl`, and encodes the encrypted file into CJK characters.
  * `decipher.sh` decrypts the file encrypted by `cipher.sh`

### `Base32CJK.py`
```
Base32CJK.py [OPTIONS]
  OPTIONS:
  -i, --in=:       input file, use stdin if not supplied
  -o, --out=:      output file
  -e, --encoding:  encode the input
  -d, --decoding:  decode the input
  -h, --help:      print this help
```
#### Encode-Decode example
For encoding a random binary file `plain.bin`:
```
cat /dev/urandom | fold -w ${1:-20} | head -n 20 > plain.bin
base32 plain.bin | python Base32CJK.py -e -o encoded.CJK.txt
```
For decoding:
```
python Base32CJK.py -d -i encoded.CJK.txt | base32 -d decoded.base32.txt > decoded.bin
```

To verify:

```
diff plain.bin decoded.bin
```

#### Compress-Decompress example

For compression a random binary file `plain.bin`:
```
cat /dev/urandom | fold -w ${1:-20} | head -n 20 > plain.bin
gzip -c plain.bin | base32 | python Base32CJK.py -e -o compressed.CJK.txt
```
For decoding:
```
python Base32CJK.py -d -i encoded.CJK.txt | base32 -d | gunzip -d > decompressed.bin
```

To verify:

```
diff plain.bin decompressed.bin
```

### Entryption-Decryption Scripts

We provide scripts `cipher.sh` and `decipher.sh` to encrypt and decrypt using [AES-256](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) with [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) implemented in `openssl`. 

```
cipher.sh <encrypted file>
decipher.sh <encrypted CJK file>
```

#### Example
For encryption:
```
./cipher.sh encrypted.txt
```
This will prompt you to enter and confirm the password, then input the text to be encrypted. If there already exists an `encrypted.txt`, you will be asked to enter the password used to encrypt this file, any new plaintext inputs will be appended to the end of the previous ones, and then encrypted. 

The encrypted text in `base32` will be saved to `encrypted.txt` and CJK-encoded `encrypted.CJK.txt`.

To decrypt the `encrypted.CJK.txt`:
```
./decipher.sh encrypted.CJK.txt
```
This will show the decrypted information on the screen, but will not write any unenscrypted info on hard disk.

## Decoding by Hand

This cipher is based on the Chinese Commercial Code, and more specifically, a subset of the code that represents a consensus of the current versions used in Mainland China, Hong Kong, Macau, and Taiwan, while allowing the variantion between traditional and simplified characters. We avoid any CCC code points that may be used to encode different characters if different code books are used. It is therefore possible to decode a CJK-text without `Base32CJK.py` if any code book is at hand. However to encode a `base32` into CJK, the concensus of CCC is required, which may not be available in the code book being used.

### Decoding Algorithm

For a given encoded CJK character, we first look up it in the code book to find its CCC code point $c$ and compute $c\equiv p \bmod 1056(=32\cdot32+32)$ with $0 \le p\in\mathbb{Z}<1056$. If $p<1024$, we can decode $p$ as two quintets (5-bit) `base32` symbols, otherwise we interpret $p \bmod 1024$ as a single quintet `base32` symbol. 

This scheme covers all double- and single-quintet strings in `base32`. To cover double- and single-sextets (6-bit) in  `base64` under this scheme, using concensus CCC is inadequate.

#### Examples

To decode the CJK character `歌`, we first identify its CCC code point $c=2960\equiv 848 \bmod1056$. Then we decode $p=848$ as two 5-bit code points $26,16$ corresponding to two `base32` symbols `2Q`.

In another example we decode the CJK character `堡` which has CCC $1027 \ge 1024$. Hence, we decode $p=1027\equiv3\bmod1024$ as a single `base32` symbol `D`.

## References

- [Unihan Database](https://unicode.org/charts/unihan.html)
- [標準電碼本(中文商用電碼), 香港商務印書館, 1972.](http://code.web.idv.hk/cccode/cccode.php)
- [中华人民共和国邮电部, 标准电码本(修订本), 人民邮电出版社, 1983.](https://zh.wiktionary.org/wiki/Appendix:%E4%B8%AD%E6%96%87%E7%94%B5%E7%A0%81/%E4%B8%AD%E5%9B%BD%E5%A4%A7%E9%99%861983)
- [RFC  4648 Base 32 alphabet](https://datatracker.ietf.org/doc/html/rfc4648#section-6)
