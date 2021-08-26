import copy, numpy as np
from random import shuffle

from Decorations import Typo


##Use Black/White text for number clues... background color for color... bold for color clue? Play around with underlining and high intensity
####################################################################################################
#########################################SETUP######################################################
####################################################################################################

Numbers=(1,1,1,2,2,3,3,4,4,5)           #GENERALIZE TO OTHER SETS OF Numbers 
#MaxNum=max(Numbers)                    #THE NUMBER 5 IS HARDCODED THROUGHOUT IN FIRST VERSION
Colors=('r','y','g','b','w')           #possibly add multi... "m"
NumColors=len(Colors)
NumPlayers=5
NumCards=4
NumTokens = 8
NumFuses = 3
ForbidEmptyClue = True                       #SET ForbidEmptyClue=True IF CLUES MUST GIVE SOME POSITIVE INFORMATION

##REALTIME VARIABLES


CClues = []                                                         #MOVE NUMBER OF COLOR CLUES ----- INCLUDED IN Actions --- DEPRECATE?
#ActiveCClues = []                                                  #JUST USE CClues AND NClues COMBINED WITH ActiveCards
NClues = []                                                         #MOVE NUMBER OF NUMBER CLUES ----- INCLUDED IN Actions --- DEPRECATE?
ActiveCards=np.reshape(range(NumPlayers*NumCards), (NumPlayers, NumCards))
#ActiveNClues = []
#DeadCards = np.zeros((NumColors, 5), int)                          #JUST Trash + Stacks... TO DEPRECATE
Trash = np.zeros((NumColors, 5), int)                               #matrix counting how many discards of each copy
PlayNext = np.asarray([[1,0,0,0,0] for i in range(NumColors)])
Extras = [[2,1,1,1,0] for i in range(NumColors)]                    #ARRAY Numbers-Ones
#LifeSpan=[(0,0) for i in range(len(Deck))]                          #MAYBE ONLY TRACK DEAD DATES OR NOT AT ALL, REPLACE TRASH HISTORY?

HistoryActiveCards = [copy.deepcopy(ActiveCards)]
HistoryCClues = [[]]
HistoryNClues = [[]]
HistoryTrash = [copy.deepcopy(Trash)]

Actions = []                                                                    #LIST ACTION TYPE FOR EVERY MOVE ACCORDING TO 0: CLUE; 1: DISCARD; 2: PLAY

TopDeck = NumCards*NumPlayers                                                   #TOP CARD AFTER THE DEAL
Tokens = NumTokens                                                              #INIT TOKENS
Fuses = NumFuses                                                                #INIT FUSES
Points = 0
Move = 0
FinalRound = False


class Player:
    def __init__(self, numcards):
        self.numcards=numcards
        self.cards=[]
        self.info={}
    _Beliefs = {}                                                       #KEY=card               VALUE IS MATRIX OF HOW Player SEES THE BELIEFS OF THE PLAYER HOLDING card
    _MetaBeliefs = {}                                                   #KEY=(card, PLAYER)     VALUE IS MATRIX OF WHAT Player BELIEVES ABOUT PLAYER'S Beliefs
    #def update():   

StrToNum={
    'r' : 0,
    'y' : 1,
    'g' : 2,
    'b' : 3,
    'w' : 4,
    'm' : 5
}

NumToDisp={
    0 : Typo.ONRED,
    1 : Typo.ONYELLOW,
    2 : Typo.ONGREEN,
    3 : Typo.ONBLUE,
    4 : Typo.ONWHITE,
    5 : Typo.ONMAGENTA
}

#CREATE AN ARRAY OF FIVE HANDS, ONE ON EACH ROW WITH CARDS REPRESENTED BY SERIAL NUMBERS FROM
#THE ORIGINAL DECK, TOP TO BOTTOM, STARTING AT 0. WE DEAL EACH HAND FROM THE TOP OF THE DECK.
#table=np.arange(20).reshape(5,4) #*******RATHER MAKE PLAYERS OBJECTS***********
#[A,B,C,D,E]=table  #MAY USE LETTERING OF PLAYERS, BUT PRLY NOT


#CREATE A FULL SHUFFLED DECK WITH NOMENCLATURE AS IN (2,0) FOR "3 red." THINK OF THE INDICES IN deck
#AS SERIAL NUMBERS WRITTEN ON THE BACKS OF THE CARDS. DeckOut CONVERTS TO EXTERNAL FORMAT LIKE "r3".
def CreateDeck():
    deck=[]
    for color in range(NumColors):
        for number in Numbers:
            deck.append((color,number-1))    #internal format numbers range 0-4; Colors are numbered
    shuffle(deck)
    deck=tuple(deck)                           #converts deck from list to tuple (mutable to immutable)
    return deck

Deck=CreateDeck()

ActiveCards = np.reshape(range(NumPlayers*NumCards),(NumPlayers, NumCards))
ColorPunch = dict.fromkeys(range(len(Deck)), np.ones((NumColors, 5), int))                               #PART OF PUBLIC DATA, BUT NEEDED FOR PRINTING
NumberPunch = dict.fromkeys(range(len(Deck)), np.ones((NumColors, 5), int))                              #key=card (serial), value = PUBLIC CARD INFO BINARY MATRIX = 1 IF POSSIBLE, 0 IF IMPOSSIBLE

PosColors = []                                                                                           #CARDS THAT HAVE BEEN CLUED POSITVE COLOR
PosNumbers = []                                                                                          #CARDS THAT HAVE BEEN CLUED POSITIVE NUMBER
Players=[]


def GiveOutCard(card):
    return Colors[card[0]]+str(card[1]+1)
def PrintOutCard(card):
    color = Deck[card][0]
    number = str(Deck[card][1]+1)
    blankspace = " "
    coloredspace = ""
    pound = ""

    if card in PosColors:
        blankspace=""
        coloredspace=" "
        if card in PosNumbers:
            pound="#"
            coloredspace=""
    elif card in PosNumbers:
        blankspace=""
        print("#", end="")
    
    print(blankspace+NumToDisp.get(color, "ERROR card {0}, color {1}: not a good color... on you...\n".format(card, color))+pound+coloredspace+number+Typo.RESET, end=" ")

def PrintDeck(deck, numcards=4, numlines=100):
    DeckOut=[GiveOutCard(card) for card in deck]
    for i in range(min(int(len(deck)/numcards)+1,numlines)):          #PRINTS DECK (numcards) AT A TIME
        for card in range(numcards*i, numcards*(i+1)):
            if card==len(deck):
                break
            PrintOutCard(card) #print(DeckOut[numcards*i:numcards*(i+1)])
        print("")

def PrintHands(includeserial=True):
    for player in range(NumPlayers):
        for card in Players[player].cards:
#            print(Deck[card][0], str(Deck[card][1]+1))
            PrintOutCard(card)
        if includeserial:
            print("")
            for card in Players[player].cards:
                print(f"{card:02}",end=" ")
        print("\n")




####################################################################################################
#####################################PUBLIC DATA####################################################
####################################################################################################

#############         stacks/PlayNext/extras***********for logging played/publicly visible cards 
#THE ARRAY stacks GIVES THE LAST NUMBER SUCCESSFULLY PLAYED FOR EACH COLOR AND extras IS A
#ManyColx5 ARRAY TELLING THE NUMBER OF EXTRAS OF EACH CARD. FOR EXAMPLE, A 5 COLOR GAME WITH ONLY
#A 1R DISCARD AND 1Y PLAYED MIGHT LOOK LIKE stacks=[0,1,0,0,0] AND
#extras=[[1,1,1,1,0],[1,1,1,1,0],[2,1,1,1,0],[2,1,1,1,0],[2,1,1,1,0]]. 


def Clue(sender, receiver, type, value):
    global Actions, Tokens, Move, ForbidEmptyClue
    emptyclue = True

    if not Tokens:
        print("ERROR: INSUFFICIENT TOKENS TO CLUE")
        return(0)
    Tokens-=1
    Actions.append(0)
    if type==0:
        yessieve=np.zeros((NumColors, 5), int)
        yessieve[value, :]=[1,1,1,1,1]
        nosieve=np.ones((NumColors, 5), int)
        nosieve[value, :]=[0,0,0,0,0]

        for card in Players[receiver].cards:
            if Deck[card][0]==value:
                PosColors.append(card)
                ColorPunch[card]*=yessieve
                emptyclue=False
            else:
                ColorPunch[card]*=nosieve
    if type==1:
        yessieve=np.zeros((NumColors, 5), int)
        yessieve[value, :]=[1,1,1,1,1]
        nosieve=np.ones((NumColors, 5), int)
        nosieve[value, :]=[0,0,0,0,0]

        for card in Players[receiver].cards:
            if Deck[card][1]==value:
                PosNumbers.append(card)
                NumberPunch[card]*=yessieve
                emptyclue=False
            else:
                NumberPunch[card]*=nosieve
    if emptyclue and ForbidEmptyClue:                                         #IF not ForbidEmptyClue, THIS ERROR SHOULD NEVER BE RAISED
        print("Empty Clue Not Allowed")
        return(0)

def Discard(player, card):
    global Actions, Tokens, TopDeck
    if Tokens==NumTokens:
        print("ERROR: CANNOT DISCARD WITH MAX NUMBER TOKENS")
        return(0)
    if card not in Players[player].cards:
        print("ERROR: CAN ONLY DISCARD FROM OWN HAND")
        return(0)
    Actions.append(1)
    Players[player].cards.remove(card)
    Players[player].cards.append(TopDeck)
    Tokens+=1
    TopDeck+=1

def Play(player, card):
    global Actions, TopDeck, Fuses, Points
    if card not in Players[player].cards:
        print("ERROR: CAN ONLY PLAY CARDS FROM OWN HAND")
        return(0)
    Actions.append(2)
    Players[player].cards.remove(card)
    Players[player].cards.append(TopDeck)
    TopDeck+=1
    if PlayNext(Deck[card]):
        Points+=1
        return(1)
    else:
        Fuses-=1
        if Fuses==0:
            print("LAST FUSE BLOWN! TRY AGAIN")
        return(Fuses)                                                    #????

for i in range(NumPlayers):
    NewPlayer=Player(NumCards)
    NewPlayer.cards=[*range(NumCards*i,NumCards*(i+1))]
    Players.append(NewPlayer)