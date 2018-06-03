# CCC Cipher
A cipher using [Chinese Commercial Code](https://en.wikipedia.org/wiki/Chinese_telegraph_code) (CCC).

## Usage
There are two components in this cipher:
* `Base64_CJK.py` encodes base64 strings into CJK strings, and decodes the original base64 from CJK codes.
* Entryptor/Decryptor
  * `cipher.sh` encrypts any file (binary or otherwise) using [AES-256](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) implemented in `openssl`, and encodes the encrypted file into CJK characters.
  * `decipher.sh` decrypts the file encrypted by `cipher.sh`

### `Base64_CJK.py`
```
Base64_CJK.py [OPTIONS]
  OPTIONS:
  -i, --in=:       input file (required)
  -o, --out=:      output file
  -e, --encoding:  encode the input
  -d, --decoding:  decode the input
  -h, --help:      print this help
```
#### Example:
For encryption:
```
base64 plaintext.txt > encoded.base64.txt
python Base64_CJK.py -e -i encoded.base64.txt -o encoded.CJK.txt
```
For decryption:
```
python Base64_CJK.py -d -i encoded.CJK.txt -o decoded.base64.txt
base64 -d decoded.base64.txt > decoded.txt
diff decoded.txt plaintext.txt
```

### Entryption/Decryption
```
cipher.sh <encrypted file>
decipher.sh <encrypted CJK file>
```

#### Example
For encryption:
```
cipher.sh encrypted.txt
```
This will prompt you to enter and confirm the password, then input the text to be encrypted. It will save the encrypted text in base64 `encrypted.txt` (which can be decrypted by openssl) and CJK-encoded `encrypted.CJK.txt`

To decrypt the `encrypted.CJK.txt`:
```
decipher.sh encrypted.CJK.txt
```
This will show the decrypted information on the screen, but not save it on hard disk.
