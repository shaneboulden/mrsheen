# mrsheen

A python script that cleans code using declared substitutions. Performs the following:

* Filename and path substitution
* File contents substitution
* RSA key and X509 certificate removal from files
* `.git` sub-directory removal

### Deployment

Create a virtual environment
```
virtualenv pyenv
source pyenv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```

### Creating a cleaned repo

Clone the code to be cleaned:
```
git clone https://github.com/peak-oss/peakoperator
```
Run `mrsheen`:
```
python mrsheen.py --dir peakoperator --json-replace substitutions.json
```
