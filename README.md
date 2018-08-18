# WebCred

Web Credibility assesment tool For Information Security Websites 
based on classified Genre.

### Demo
This application is deployed [here](https://serc.iiit.ac.in/webcred/) 
for testing purpose.

### Developement

Further development of this tool is available [here](https://github.com/SIREN-SERC/WEBCred)

## Installation
- Run pipenv 
   - `$: install pipenv` and enter the `shell`

- Install [postgres](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04)

- Configure postgres:
   - Create new db
        
        `$: create database __name__`
   - Create password for postgresql
        
        `$: psql postres`
        
        `$: \password`

- Populate the environment variables listed in `env.sample` into `.env` 
with correct values.

-  Install [JDK](http://www.oracle.com/technetwork/java/javase/downloads/jdk10-downloads-4416644.html)

- Download Stanford CoreNLP Library
    
  - `$: wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-02-27.zip`

  - `$: unzip stanford-corenlp-full-2018-02-27.zip -d stanford-corenlp-full`

- nltk packages:

    ```
    import nltk
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('stopwords')
    ```

## Test

Start the webserver - `$: python app.py`
    