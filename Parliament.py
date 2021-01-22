from selenium import webdriver
from bs4 import BeautifulSoup
import re
import requests
import sys
import pdfminer
import urllib
import fitz
from io import StringIO
from io import BytesIO
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from lxml import etree as et
from tqdm import tqdm
import pickle
import textract
import PyPDF2
from tika import parser
import validators


"""
    First initialize some useful functions

    natural_keys; atoi - functions that the class will use to sort statements

    review - takes a list of statements and allows you to inspect them one by one.
        Pass the word 'end' to kill this function.
"""
def atoi(text):                                 # Utility
    return int(text) if text.isdigit() else text

def natural_keys(text):                         # Utility
    return [atoi(c) for c in re.split(r'(\d+)', text[0][11:16])]

def review(name):
    curr = 0                    # Variable that stores the number of the current utterance
    while curr !='end':
        curr = input()          # Choose which utterance to inspect

        if curr == 'delete':    # delete utterance
            curr= input()
            del orationes[curr]
            continue

        if curr == 'len':       # See how many utterances are in the list
            print(len(name))
            continue

        try:
            print(name[int(curr)])  # Tries to print the utterance under the current number

        except:                     # If the list is shorter than the called number - prints the list's length
            print(f'Out of reach. The max is {len(name)-1}')





class Parliament:
    def __init__(self,path):
        """

        Opens the browser and accesses the government website

        Initializes class variables

        Sets up data folders in the directory with which the class was initialized

        path = directory


        """
        driver = webdriver.Chrome("/Users/hubertplisiecki/PycharmProjects/NLP/chromedriver")    # loads the chromedriver (needed to run)

        driver.get("https://www.sejm.gov.pl/sejm9.nsf/stenogramy.xsp")             # loads the governmetnal website

        self.path = path                # the path that was passed into the class

        self.orationes = []             # variable that will store statement        (Orationes - parliament statements from latin)

        self.osoby = []                 # variable that will store all members of the parliament

        content = driver.page_source    # loads the contents of the website initialized earlier

        self.soup = BeautifulSoup(content, features='html.parser') # converts the contents of the website to BeautifulSoup format

        self.number = 54                # number of proceedings (can be automatized)

        self.finder = []                # a list that will store the names of the politician that who's statements are currently of interest

        self.digits = re.compile('[0-9][0-9][0-9]')     # Useful constants intiialized here
        self.digitu = re.compile('[0-9][0-9]')          #     for more clarity later
        self.digit = re.compile('[0-9]')                #

        try:
            os.mkdir(path + 'parliament' + '/html')
            os.mkdir(path + 'parliament' + '/txt')
            os.mkdir(path + 'parliament' + 'pis')
            os.mkdir(path + 'parliament' + 'ko')
            os.mkdir(path + 'parliament' + 'psl')                  #   Tries to create folders
            os.mkdir(path + 'parliament' + 'lewica')
            os.mkdir(path + 'parliament' + 'konfederacja')
            os.mkdir(path + 'parliament' + 'mn')
            os.mkdir(path + 'parliament' + 'rest')
            os.mkdir(path + 'parliament' + 'savedata')

        except:                                              #   Does not create folders if they were already created
            pass

    def checker(self,name):
        """

        Used to find a name of a certain politician and fill the self.finder variable with it in order
        to look up his statements later.

        Takes the name of the politician (str) displays matching names and asks for input. If the input is 'y'
        it appends the name to the self.finder variable.

        name(str) = name of the politician

        """
        for i in self.osoby:                            # Looks for a similar name in the parliament members list
            if name in i[0]:

                print(i)                                # Shows what it has found

                if input()=='y':                        # Asks you for permission to add it to the finder
                    self.finder.append(i[0])


    def convert_pdf_to_html(self):
        """

        Converts the pdf that is currently stored in the temporary file inside the repository to an html object

        """
        rsrcmgr = PDFResourceManager()          # Magic (simply functional)
        retstr = BytesIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(self.path+'parliament/repository/temp.pdf', 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)
        fp.close()
        device.close()
        self.text = retstr.getvalue()
        retstr.close()

    def khkhm(self):
        """

        Clears the lists containing the names and statements of the politicians.

        """
        self.orationes = []
        self.finder = []

    def load(self):
        """

        Downloads all proceeding files from the governmental website and stores them in specified folders.
        (May take long to compute)

        """
        title = 1

        # Opens each pdf file present on the governmental website

        for a in tqdm(self.soup.findAll('a', href=True, attrs={'class': 'pdf'})):
            url = a.get('href')
            urllib.request.urlretrieve(url, self.path+'parliament/repository/temp.pdf')
            self.convert_pdf_to_html()                                         # Converts them first to the html format

            with open(self.path + f'parliament/html/{title}.pickle', 'wb') as f:
                pickle.dump(self.text, f, pickle.HIGHEST_PROTOCOL)                  # and saves

            file_data = parser.from_file(self.path)
            self.text = file_data['content']                                   # Then to the txt format

            with open(self.path +f'parliament/txt/{title}.pickle', 'w') as f:
                f.write(self.text)                                                  # and saves
            title+=1
            self.number = title

    def orator(self):
        """

        Loads all the statements made by the politician who's name is currently in the self.finder variable

        """
        rue = self.path + 'parliament/rest/' + self.finder[0] + '/.pkl'      # Modifies the path to load from
        if self.finder in self.pis:
            rue = self.path + 'parliament/pis/' + self.finder[0] + '.pkl'
        if self.finder in self.ko:
            rue = self.path + 'parliament/ko/' + self.finder[0] + '.pkl'
        if self.finder in self.psl:
            rue = self.path + 'parliament/psl/' + self.finder[0] + '.pkl'
        if self.finder in self.lewica:
            rue = self.path + 'parliament/lewica/' + self.finder[0] + '.pkl'
        if self.finder in self.konfederacja:
            rue = self.path + 'parliament/konfederacja/' + self.finder[0] + '.pkl'
        if self.finder in self.mn:
            rue = self.path + 'parliament/mn/' + self.finder[0] + '.pkl'

        with open(rue, 'rb') as f:                                           #  Loads
            self.orationes = pickle.load(f)

    def party(self, name):
        """

        Searches for all the party member's statements and saves them in specific folders.

        self.name = name of the party (pis / ko / psl / lewica / konfederacja / mn / rest)


        """
        if name == 'pis':
            party = self.pis
        if name == 'ko':
            party = self.ko                             # Checks which party was called
        if name == 'psl':
            party = self.psl
        if name == 'lewica':
            party = self.lewica
        if name == 'konfederacja':
            party = self.konfederacja
        if name == 'mn':
            party = self.mn
        if name == 'rest':
            party = [['Duda:'],['Marszałek:']]

        self.khkhm()                                        # Clears variables

        count = 0
        for i in tqdm(party):                               # Searches for the statements made by each of the
            count+=1                                        #   party members
            self.finder = i
            self.rostrum()
            if len(self.orationes)>0:                       # Ignores the members who did not speak at all

                ordered = self.sort()                       # Sorts the statements

                self.save(ordered,i[0],name)                # Saves the statements of each of the party
                self.khkhm()                                #   members

    def rostrum(self):
        """

        Uses the self.finder variable to find all the statements made by the politicians contained in it.
        Makes a call to the voice() function.

        """
        for i in tqdm(range(self.number)):        # Opens each proceeding file
            i+=1
            with open(f'/Users/hubertplisiecki/PycharmProjects/NLP/parliament/html/{i}.pickle', 'rb') as f:
                self.html = pickle.load(f)
            with open(f'/Users/hubertplisiecki/PycharmProjects/NLP/parliament/txt/{i}.txt', 'r') as f:
                self.txt = f.read()
            self.zupa = BeautifulSoup(self.html)

            self.voices()                         # And looks for the statement made by the politician in each of them

        self.orationes = list(dict.fromkeys(self.orationes))    # Deletes duplicates

    def save(self,object,title,dir):
        """

        Saves an object in a certain subfolder.

        object = object (list, string, whatever)
        title = the title of the created file
        dir = subdirectory; usually one of these: pis / ko / lewica / psl / konfederacja / mn / repository

        """
        with open(self.path + f'parliament/{dir}/' + f'{title}.pkl', 'wb') as f:
            pickle.dump(object, f)

    def set(self):
        """

        Loads the lists of parliament members.

        Should be called everytime just after the class is initialized (unless the variables have not been procured yet)

        self.osoby = all members
        self.pis = members elected from the PiS elective lists
        self.ko = members elected from the KO elective lists
        self.psl = members elected from the PSL elective lists
        self.lewica = members elected from the elective lists of "Lewica"
        self.konfederacja = members elected from the elective lists of "Konfederacja"
        self.MN = members elected from the elective list of the German minority


        """
        with open(self.path + 'parliament/repository/os.pkl', 'rb') as f:     # Just loads variables
            self.osoby = pickle.load(f)
        with open(self.path + 'parliament/repository/pis.pkl', 'rb') as f:
            self.pis = pickle.load(f)
        with open(self.path + 'parliament/repository/ko.pkl', 'rb') as f:
            self.ko = pickle.load(f)
        with open(self.path + 'parliament/repository/psl.pkl', 'rb') as f:
            self.psl = pickle.load(f)
        with open(self.path + 'parliament/repository/lewica.pkl', 'rb') as f:
            self.lewica = pickle.load(f)
        with open(self.path + 'parliament/repository/konfederacja.pkl', 'rb') as f:
            self.konfederacja = pickle.load(f)
        with open(self.path + 'parliament/repository/mn.pkl', 'rb') as f:
            self.mn = pickle.load(f)

    def sort(self):
        """

        Sorts the content of the self.orationes variable and outputs statements sorted by date and time.

        """
        self.orationes.reverse()  # First reverses the order of the statement list
        split = [i.splitlines()[0] for i in self.orationes]  # Creates an alternative list which contains only
        count = 0  # the statement dates
        for i in range(len(split[:])):  #
            split[i] = str(i) + '   ' + split[i]  # Numbers the dates so that they can be later used
            count += 1  # to order the original list
        curr = split[0][-20:]
        full = []
        temp = []
        for i in split:  # Creates an embedded list where the statements
            if i[-20:] != curr:  # that were uttered on the same day are grouped
                curr = i[-20:]  # together
                full.insert(0, temp)
                temp = [i]
            else:
                temp.append(i)
        full.insert(0, temp)
        first = [['stycznia'], ['lutego'], ['marca'], ['kwietnia'], ['maja'], ['czerwca'], ['lipca'], ['sierpnia'],
                 ['września'], ['października'], ['listopada'], ['grudnia']]
        for i in full:
            stop = False  # Embedds the list one more time, this time
            for j in range(len(first)):  # storing the lists of utterances made in the same
                if first[j][0] in i[0]:  # month together.
                    first[j].append(i)
                    stop = True
                if stop == True:
                    break

        for i in first:  # Sorts the elements of each of the month lists
            del i[0]  # according to the order of the days on which they were
            i = i.sort(key=natural_keys)  # uttered.

        ordered = sum(first, [])
        ordered = sum(ordered, [])                     # Flattens the list
        numbers = [int(i[0:3].replace(' ', '')) for i in ordered]
        new = []

        for i in numbers:                               # Sorts the actual utterances
            new.append(self.orationes[i])

        return new                                      # Returns a list of sorted utterances

    def voices(self):
        """

        Finds all statements made by the politician, who's name is currently stored in the self.finder variable
        and saves them as the orationes list

        """
        for name in self.finder:            # an artifact, maybe useful later
            read = False                    # The algorithm will read every line for which the read var will be Trure
            b = self.zupa.body.find(text=re.compile('t e n o g r a f i c z n e'))   # Used to easily get the date
            head = b.parent.parent.next_sibling.next_sibling.get_text() + '\n'      # of the proceeding
            for line in self.txt.splitlines():
                if name in line.strip().split()[-1:]:
                    read = True                             # In basic terms: for each line in the string
                    voice=''                                # see if the searched name is present
                    continue                                # and read all of the next lines if it is
                if read == True:

                    #   Until certain key words or another politician's name is encountered:

                    if line.strip().split()[-1:] in self.osoby or ('(Marszałek' and 'trzykrotnie' and 'uderza' and 'laską' in line) or ('(Przerwa w posiedzeniu o godz.' in line):
                        clean = head
                        for verse in voice.splitlines()[:]:         # Then split the recovered statement
                            find = False
                            for os in self.osoby:
                                if os[0] in verse and '(' not in verse:
                                    find = True
                            if find == True:
                                break

                            # And clean it:

                            if ('Informacja' and 'dla' and 'Sejmu' and 'i' and 'Senatu' and 'RP') and ('(Początek' and 'posiedzenia') and ('Spis' and 'treści') and ('posiedzenie' and 'Sejmu' and 'w' and 'dniu') not in verse:
                                if len(verse)>4:
                                    if validators.url(verse.strip())!=True:
                                        if verse.strip() != ('Sp' and 'is' and 't' and 're' and 'śc' and 'i'):
                                            if 'Page' not in verse:
                                                if re.match(self.digits, verse) == None and re.match(self.digitu,verse) == None and re.match(self.digit, verse) == None:
                                                    if verse != '':
                                                        clean = clean + verse + '\n'

                        # Finally append it to the self.orationes variable

                        self.orationes.append(clean)
                        read = False                            # and set read back to False
                        continue
                    voice += line + '\n'















sejm = Parliament('/Users/hubertplisiecki/PycharmProjects/NLP/')    # Initialize the function with the directory that
                                                                   #    you would like to use

sejm.load()         # Start by downloading the proceeding files
