# CCC Cipher
A cipher using [Chinese Commercial Code](https://en.wikipedia.org/wiki/Chinese_telegraph_code) (CCC).

## Usage
There are two components in this cipher:
* `Base32CJK.py` encodes base32 strings into CJK strings, and decodes the original base32 from CJK codes. Note that the encoding does not work for base64.
* Entryptor/Decryptor
  * `cipher.sh` encrypts any file (binary or otherwise) using [AES-256](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) with [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) implemented in `openssl`, and encodes the encrypted file into CJK characters.
  * `decipher.sh` decrypts the file encrypted by `cipher.sh`

### `Base32CJK.py`
```
Base32CJK.py [OPTIONS]
  OPTIONS:
  -i, --in=:       input file (required)
  -o, --out=:      output file
  -e, --encoding:  encode the input
  -d, --decoding:  decode the input
  -h, --help:      print this help
```
#### Example:
For encoding :
```
base32 plaintext.txt > encoded.base32.txt
python Base32CJK.py -e -i encoded.base32.txt -o encoded.CJK.txt
```
For decoding:
```
python Base32CJK.py -d -i encoded.CJK.txt -o decoded.base32.txt
base32 -d decoded.base32.txt > decoded.txt
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
./cipher.sh encrypted.txt
```
This will prompt you to enter and confirm the password, then input the text to be encrypted. If there already exists an `encrypted.txt`, you will be asked to enter the password used to encrypt this file, any new plaintext inputs will be appended to the end of the previous ones, and then encrypted. 

The encrypted text in base32 will be saved to `encrypted.txt` and CJK-encoded `encrypted.CJK.txt`.

To decrypt the `encrypted.CJK.txt`:
```
./decipher.sh encrypted.CJK.txt
```
This will show the decrypted information on the screen, but will not save it on hard disk.
