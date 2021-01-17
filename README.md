# Parliament
Python script that scrapes the website of the Polish government for pdfs with the audiodescriptions of parliament proceesings. It sorts the text according to the author of the statement.


This code can be run as a whole or used in bits via the python console.

In order to run it, the "parliament" file with the "repository" subfile has to be downloaded. 
It's directory should be passed to the class in order to initialize it

Class Parliament -> Main class of the project. Initialisation creates the required file infrastructure by itself. All that is needed for it to run is to 
download the Parliament folder, with the repository inside and pass the directory in which it was nested to the class initialiser.
The class includes the following functions (sorted alphabetically) :

- checker -> find the politician you would like to search for and adds him to the cache

- convert_to_html -> converts to html (utility)

- khkhm -> clears the cache ( does not clear the cache loaded by the set() function)

- load -> downloads all of the pdfs and transforms them (takes some time)

- orator -> searches for the utterances of the politician that is stored in the cache (if the utterances have been already parsed)

- party -> parses the downloaded pdfs for utterances made by politicians of a certain party (takes some time)

- rostrum -> parses the downloaded pdfs for utterances made by the politician who is currently stored in the cache

- save -> saves a certain object in a certain subdirectory

- set -> downloads cache from the repository subfile

- sort -> sorts the utterances currently stored in the cache

- voices -> parses the current pdf file for utterances made by the politician that is currently stored in the cache

For more information on how to use these functions see code description.

# Word Vectors

Here are simple word vectors trained on all the utterances from the 2020 parliament proceedings.
They are not lemmatized on purpose.

![alt text](https://github.com/hplisiecki/Parliament/blob/2ba00f41573fd14616138c64042dcdbfad788e4a/Screenshot%202021-01-17%20at%2013.25.17.png)
