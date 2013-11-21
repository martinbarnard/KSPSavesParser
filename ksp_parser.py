#!/usr/bin/env python
from argparse import ArgumentParser


def grabKV(line):
    nline=line.split("=")
    nline[0]=nline[0].strip()
    nline[1]=nline[1].strip()
    if len(nline)>1:
        try:
        # check our args for ","
            bob=nline[1].find(u',')
            if bob >=0:
                v=nline[1].split(u',')
                nline[1]=v

        except:
            return nline
        return nline
    else:
        print 20*"*","grabKV error with {}".format(line)
        return line

def open_file(fn):
    '''
    returns a list of lines in the given file, or None
    '''
    import os
    print "trying to use {}".format(fn)
    try:
        f=open(fn,'r')
        lines=f.readlines()
        f.close()
    except:
        print "Unable to open {}. Quitting".format(fn)
        lines=[]
    return lines

class Token(object):
    def __init__(self, tokenName='', lineNumber=0, lines=[], recursionID=0):
        self.tokens={}
        self.values={}
        self.classifiers={}
        self.lineNumber=lineNumber
        self.lines=lines
        self.tokenName=tokenName
        self.recursionID=recursionID
        # we don't call nextLine here, because it's line 0, and nextLine increments
        # linenumber by 1 BEFORE running
        if len(self.lines)>self.lineNumber:
            self.current_line=self.clean_line(lines[lineNumber])
            self.current_line_type=self.testLine()
            self.grabValues()
        else:
            self.lineNumber=-1
            raise EOFError, "end of file"

    def printValues(self, tabStr='-'):
        if len(self.values.keys())>0:
            for k in sorted(self.values.keys()):
                if type(self.values[k])==type([]):
                    print "{} {} :: {} = ".format(tabStr, self.tokenName, k),
                    print ">>>{}".format(self.values[k])
                else:
                    print "{} {} :: {} = {}".format(tabStr, self.tokenName,k,self.values[k])
        else:
            print "{}No values in {}".format(tabStr, self.tokenName)

    def printTokens(self, tabStr='-', withValues=True):
        if len(self.tokens.keys())>0:
            for k in sorted(self.tokens.keys()):
                print "{} token {}".format(tabStr,k)
                self.tokens[k].printMe(tabStr+'-')


    def printMe(self, tabStr='-'):
        self.printValues(tabStr)
        self.printTokens(tabStr)
    def clean_line(self, line):
        line=line.strip().strip('\n').strip('\t')
        return line
    def nextLine(self):
        if  self.lineNumber>=0:
            self.lineNumber+=1
            if len(self.lines)>=self.lineNumber:
                try:
                    self.current_line=self.clean_line(self.lines[self.lineNumber])
                    self.current_line_type=self.testLine()
                except IndexError:
                    print "...parsed..."#print "end of lines error"
                    self.lineNumber=-1
            else:
                self.lineNumber=-1

    def grabValues(self):
        '''
        Meat of our class. This iterates through our lines & farms out to wherever they
        should go
        '''
        if  self.lineNumber >=0:
            while self.current_line_type !='}' and not self.lineNumber==-1:
                if self.current_line_type=='{':         # this should always be skipped
                    self.nextLine()                     # increments by one, so should be at token name
                elif self.current_line_type=='equals':  # is a key/value pair
                    tt=grabKV(self.current_line)
                    self.values[tt[0]]=tt[1]
                    self.nextLine()                     # pull our next line into our buffer
                elif self.current_line_type=='token':   # starts a token
                    token_name="{}_{}".format(self.current_line, self.lineNumber)
                    self.nextLine()
                    newToken=Token(token_name, self.lineNumber, self.lines, self.recursionID+1)
                    #print "R{}, Adding token {} to {} at line {}".format(self.recursionID*"-", token_name, self.tokenName, self.lineNumber)
                    self.tokens[token_name]=newToken
                    # update our line number with child
                    #print "updating linenumber from {} to {}".format(self.lineNumber, self.tokens[token_name].lineNumber)
                    self.lineNumber=self.tokens[token_name].lineNumber
                    if not self.lineNumber==-1:
                        self.nextLine()
                    else:
                        #print "Leaving grabValues[{}]".format(self.tokenName)
                        break
                else:
                    break
        else:
            return -1
        return self.lineNumber



    def testLine(self):#, firstchars="{}", anychars="="):
        '''
        takes a line & tests for given chars
        returns token line, equal anychars, or brace 1/2 where 1 is open & 2 is closed
        '''
        char=self.current_line[0]
        try:
            if char != u'{' and char != u'}':
                bob=self.current_line.find(u'=')
                #print "bob is {}, char is {}".format(bob, char)
                if self.current_line.find(u'=')==-1:
                    return 'token'
                else:
                    return 'equals'
            else:
                if char==u'{':
                    return '{'
                else:
                    return '}'
        except UnicodeDecodeError:
            return 'equals' # probably
def main(fileName):
    lines=open_file(fileName)
    if lines:
        token=Token('',0,lines)
    if token:
        token.printMe()

if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('-f', '--file', dest="fileName",
            help="Use FILE savefile", metavar="FILE",
            default='persistent.sfs')
    args=parser.parse_args()
    main(args.fileName)

