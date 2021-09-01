import copy, numpy as np
from random import shuffle

from Decorations import *


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
MaxTokens = False
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
Discards = []
Stacks=[0 for i in range(NumColors)]
TopStacks=[NumColors*len(Numbers)+i for i in range(NumColors)]                 #DUMMY 0 CARDS AT END OF DECK FOR PRINTING OUT STACKS BEFORE 1 IS PLAYED
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
    #deck=tuple(deck)                           #converts deck from list to tuple (mutable to immutable)
    return deck

Deck=tuple(CreateDeck()+[(i,-1) for i in range(NumColors)])

ActiveCards = np.reshape(range(NumPlayers*NumCards),(NumPlayers, NumCards))
ColorPunch = dict.fromkeys(range(len(Deck)), np.ones((NumColors, 5), int))                               #PART OF PUBLIC DATA, BUT NEEDED FOR PRINTING
NumberPunch = dict.fromkeys(range(len(Deck)), np.ones((NumColors, 5), int))                              #key=card (serial), value = PUBLIC CARD INFO BINARY MATRIX = 1 IF POSSIBLE, 0 IF IMPOSSIBLE

PosColors = []                                                                                           #CARDS THAT HAVE BEEN CLUED POSITVE COLOR
PosNumbers = []                                                                                          #CARDS THAT HAVE BEEN CLUED POSITIVE NUMBER
Players=[]

for i in range(NumPlayers):
    NewPlayer=Player(NumCards)
    NewPlayer.cards=[*range(NumCards*i,NumCards*(i+1))]
    Players.append(NewPlayer)

#def GiveOutCard(card):
#    return Colors[card[0]]+str(card[1]+1)
def PrintOutCard(card, blinded=False):
    color = Deck[card][0]
    if blinded and card not in PosNumbers:
        number = 'X'
    else:
        number = Typo.BOLD+str(Deck[card][1]+1)
    blankspace = " "
    coloredspace = ""
    pound = ""
    if card in PosColors:
        blankspace=""
        coloredspace=" "
        if card in PosNumbers and not blinded:
            pound="#"
            coloredspace=""
    elif card in PosNumbers and not blinded:
        blankspace=""
        print("#", end="")
    
    print(blankspace+NumToDisp.get(color, "ERROR card {0}, color {1}: not a good color... on you...\n".format(card, color))+pound+coloredspace, end="")
    if not blinded or card in PosColors:
        print(number+Typo.RESET, end=" ")
    else:
        print(Typo.RESET+number, end=" ")

def PrintDeck(deck, numcards=4, numlines=100):
    DeckOut=[GiveOutCard(card) for card in deck]
    for i in range(min(int(len(deck)/numcards)+1,numlines)):          #PRINTS DECK (numcards) AT A TIME
        for card in range(numcards*i, numcards*(i+1)):
            if card==len(deck):
                break
            PrintOutCard(card) #print(DeckOut[numcards*i:numcards*(i+1)])
        print("")

def PrintHands(currentplayer, blinded=True, includeserial=True):
    for player in range(NumPlayers):
        print("Player {0} :    ".format(player), end="")
        for card in Players[player].cards:
            if player==currentplayer:
                PrintOutCard(card, blinded)
            else:
                PrintOutCard(card)
        if includeserial:
            print("\n              ".format(player), end="")
            for card in Players[player].cards:
                print(f"{card:02}",end=" ")
        print("\n")
    print("SCORE: {0}  TOKENS: {1}".format(sum(Stacks), Tokens), end="")
    print("       STACKS : ", end="")
    for color in range(NumColors): PrintOutCard(TopStacks[color])
    print("       DISCARDS:       ", end="")
    for card in Discards: PrintOutCard(card)
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
        raise ValueError("ERROR: INSUFFICIENT TOKENS TO CLUE")
    if sender==receiver:
        raise ValueError("ERROR: CANNOT CLUE SELF")
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
        raise ValueError("ERROR: CLUE MUST BE POSITIVE :)")

def Discard(player, card):
    global Actions, Tokens, TopDeck
    if Tokens==NumTokens and MaxTokens:
        raise ValueError("ERROR: CANNOT DISCARD WITH MAX NUMBER TOKENS")
    if card not in Players[player].cards:
        #print("Players[player].cards is ", Players[player].cards)
        #print("truth statement card in Players[player].cards", card in Players[player].cards)
        raise ValueError("ERROR: CAN ONLY DISCARD FROM OWN HAND")
    Actions.append(1)
    Players[player].cards.remove(card)
    Players[player].cards.append(TopDeck)
    Discards.append(card)
    Tokens+=1
    TopDeck+=1

def Play(player, card):
    global Actions, TopDeck, Fuses, Points
    if card not in Players[player].cards:
        raise ValueError("ERROR: CAN ONLY PLAY CARDS FROM OWN HAND")
    Actions.append(2)
    Players[player].cards.remove(card)
    Players[player].cards.append(TopDeck)
    TopDeck+=1
    if PlayNext[Deck[card]]:
        Points+=1
        #Stacks[Deck[card][0]]+=1
        TopStacks[Deck[card][0]]=card
    else:
        Fuses-=1
        Discards.append(card)
        if Fuses==0:
            raise Exception("LAST FUSE BLOWN! TRY AGAIN")

def ManualTakeAction(currentplayer):
    action = input("Player {0} to play: ".format(currentplayer+1))
    action=action.split(" ")
    if action[0].lower()=='clue':
        if type(action[2]) is str and action[2].lower()=='col':
            print('Cluing Player {0} about {1} {2}'.format(action[1], 'color', action[3]))
            Clue(currentplayer, int(action[1])-1, 0, StrToNum.get(action[3], "enter color r, y, g, b, w, m"))
        elif type(action[2]) is str and action[2].lower()=='num':
            print('Cluing Player {0} about {1} {2}'.format(action[1], 'number', action[3]))
            Clue(currentplayer, int(action[1])-1, 1, int(action[3])-1)
        else:
            print("INVALID CLUE")
    elif action[0].lower()=="discard":
        Discard(currentplayer, int(action[1]))
    elif action[0].lower()=='play':
        Play(currentplayer, int(action[1]))
    else:
        raise ValueError("INVALID PLAY")
