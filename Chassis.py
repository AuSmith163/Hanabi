import copy, numpy as np
from random import shuffle

from Decorations import *

#FOR DISPLAY, THE SYMBOL "#" DENOTES A CARD THAT IS CLUED NUMBER AND UNDERLINED DENOTES ONE CLUED
#COLOR. INPUT A CLUE PLAY AS EITHER "clue" FOLLOWED BY A SPACE AND THE RECEIVER'S PLAYER NUMBER
#THEN THE CLUE AS IN "1 2 3 4 5" OR "r o y g b m" AGAIN SEPARATED BY SINGLE SPACES. INPUT A DISCARD
#OR A PLAY by "discard" OR "play" FOLLOWED BY THE SERIAL NUMBER DISPLAYED BENEATH THE CARD.

#OFTEN, BINARY MATRICES ARE USED TO RECORD THE POSSIBILITIES FOR CARDS IN ONES OWN HAND, OR FOR WHAT
#ONE PLAYER BELIEVES OTHER PLAYERS BELIEVE ABOUT THEIR CARDS, ETC.

####################################################################################################
#########################################SETUP######################################################
####################################################################################################

class Parameters:
    Numbers=(1,1,1,2,2,3,3,4,4,5)               #ABLE TO GENERALIZE TO OTHER SETS OF Numbers 
    MaxNum=max(Numbers)                         #THE NUMBER 5 IS HARDCODED THROUGHOUT THE FIRST VERSION
    Colors=('r','y','g','b','w')                #POSSIBLY ADD 'm' FOR THE MULTICOLOR SET
    NumColors=len(Colors)
    NumPlayers=5
    NumCards=4                                  #NUMBER OF CARDS PER HAND
    NumTokens = 8
    MaxTokens = False                           #IF NumTokens IS THE MAXIMUM NUMBER OF POSSIBLE Tokens
    NumFuses = 3
    AutoPlay=[]                                 #COMPUTER PLAYERS
    ForbidEmptyClue = True                      #ForbidEmptyClue==True IF CLUES MUST GIVE SOME POSITIVE INFORMATION
    NumDistinctCards = NumColors*MaxNum         #TOTAL NUMBER OF CARDS



##REALTIME VARIABLES

class PublicInfo:
    CClues = []                                                         #MOVE NUMBER OF COLOR CLUES ----- INCLUDED IN Actions --- DEPRECATE?
    #ActiveCClues = []                                                  #JUST USE CClues AND NClues COMBINED WITH ActiveCards
    NClues = []                                                         #MOVE NUMBER OF NUMBER CLUES ----- INCLUDED IN Actions --- DEPRECATE?
    ActiveCards=np.reshape(range(Parameters.NumPlayers*Parameters.NumCards), (Parameters.NumPlayers, Parameters.NumCards))
    #ActiveNClues = []
    Trash = np.zeros((Parameters.NumColors, 5), int)                                            #MATRIX COUNTING HOW MANY DISCARDS OF EACH COPY
    Discards = []
    Stacks=[0 for i in range(Parameters.NumColors)]
    TopStacks=[i - Parameters.NumColors for i in range(Parameters.NumColors)]                   #DUMMY 0 CARDS AT END OF DECK FOR PRINTING
    PlayNext = np.asarray([[1,0,0,0,0] for i in range(Parameters.NumColors)])                   #OUT STACKS BEFORE 1 IS PLAYED
    Extras = [[2,1,1,1,0] for i in range(Parameters.NumColors)]          #ARRAY Numbers-Ones
    #LifeSpan=[(0,0) for i in range(len(Deck))]                          #MAYBE ONLY TRACK DEAD DATES OR NOT AT ALL, REPLACE TRASH HISTORY?

    HistoryActiveCards = [copy.deepcopy(ActiveCards)]
    HistoryCClues = [[]]
    HistoryNClues = [[]]
    HistoryTrash = [copy.deepcopy(Trash)]

    Actions = []                                                         #LIST ACTION TYPE FOR EVERY MOVE ACCORDING TO 0: CLUE; 1: DISCARD; 2: PLAY

class GameState:
    TopDeck = Parameters.NumDistinctCards                                #TOP CARD AFTER THE DEAL
    Tokens = Parameters.NumTokens                                        #INITIAL TOKENS
    Fuses = Parameters.NumFuses                                          #INITIAL FUSES
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

#CREATE AN ARRAY OF NumPlayers MANY HANDS, ONE ON EACH ROW WITH CARDS REPRESENTED BY SERIAL NUMBERS FROM
#THE ORIGINAL DECK, TOP TO BOTTOM, STARTING AT 0. WE DEAL EACH HAND FROM THE TOP OF THE DECK.
#CREATE A FULL SHUFFLED DECK WITH NOMENCLATURE AS IN (0,2) FOR "COLOR 0 AND NUMBER 2+1" OR JUST "red 3"
#THINK OF THE INDICES IN Deck AS SERIAL NUMBERS WRITTEN ON THE BACKS OF THE CARDS.

def CreateDeck():
    deck=[]
    for color in range(Parameters.NumColors):
        for number in Parameters.Numbers:
            deck.append((color,number-1))    #INTERNAL FORMAT COLORS AS INTEGERS (CONVERT USING StrToNum)
    shuffle(deck)
    return deck

Deck=tuple(CreateDeck()+[(i, -1) for i in range(Parameters.NumColors)])

ActiveCards = np.reshape(range(Parameters.NumPlayers*Parameters.NumCards),(Parameters.NumPlayers, Parameters.NumCards))
ColorPunch = dict.fromkeys(range(len(Deck)), np.ones((Parameters.NumColors, 5), int))
NumberPunch = dict.fromkeys(range(len(Deck)), np.ones((Parameters.NumColors, 5), int))                   #key=card (serial), value = PUBLIC CARD INFO BINARY MATRIX = 1 IF POSSIBLE, 0 IF IMPOSSIBLE

PosColors = []                                                                                           #CARDS THAT HAVE BEEN CLUED POSITVE COLOR
PosNumbers = []                                                                                          #CARDS THAT HAVE BEEN CLUED POSITIVE NUMBER
Players=[]

for i in range(Parameters.NumPlayers):
    NewPlayer=Player(Parameters.NumCards)
    NewPlayer.cards=[*range(Parameters.NumCards*i,Parameters.NumCards*(i+1))]
    Players.append(NewPlayer)


####################################################################################################
########################################DISPLAY#####################################################
####################################################################################################


def DispCard(card, blinded=False):
    color = Deck[card][0]
    result=Typo.BOLD
    if blinded and card not in PosNumbers:
        number="X"
    else:
        number=str(Deck[card][1]+1)
    if not blinded or card in PosColors:
        result+=NumToDisp[color]
    if card in PosColors and not blinded:
        result+=Typo.UNDERLINE
    if card in PosNumbers and not blinded:
        result+="#"
    else:
        result+=" "
    
    if not blinded or card in PosColors:
        result+=number+Typo.RESET+" "
    else:
        result+=Typo.RESET+number+" "
    return(result)

def ReturnDeck(deck, numcards=4, numlines=100):
    DeckOut=[Colors[card[0]]+str(card[1]+1) for card in deck]
    result=""
    for i in range(min(int(len(deck)/numcards)+1,numlines)):          #PRINTS DECK (numcards) AT A TIME
        for card in range(numcards*i, numcards*(i+1)):
            if card==len(deck):
                break
            result+=DispCard(card) #print(DeckOut[numcards*i:numcards*(i+1)])
        result+="\n"
    return(result)

def Hands(blinded=[], includeserial=True):
    result=""
    for player in range(Parameters.NumPlayers):
        result+="Player {0} :    ".format(player+1)
        for card in Players[player].cards:
            if player in blinded:
                result+=DispCard(card, True)
            else:
                result+=DispCard(card)
        if includeserial:
            result+="\n              ".format(player)
            for card in Players[player].cards:
                result+=f"{card:02}"+" "
        result+="\n"
    result+="SCORE: {0}  TOKENS: {1}  FUSES: {2}".format(sum(PublicInfo.Stacks), GameState.Tokens, GameState.Fuses)
    result+="       STACKS : "
    for color in range(Parameters.NumColors): result+=DispCard(PublicInfo.TopStacks[color])
    result+="       DISCARDS:       "
    for card in PublicInfo.Discards: result+=DispCard(card)
    result+="\n"
    return(result)



####################################################################################################
#####################################PLAY OPTIONS###################################################
####################################################################################################



def Clue(sender, receiver, type, value):
    #global Actions, Tokens, Move, ForbidEmptyClue
    emptyclue = True
    if not GameState.Tokens:
        return("ERROR: INSUFFICIENT TOKENS TO CLUE")
    if sender==receiver:
        return("ERROR: CANNOT CLUE SELF")
    GameState.Tokens-=1
    PublicInfo.Actions.append(0)
    if type==0:
        yessieve=np.zeros((Parameters.NumColors, 5), int)
        yessieve[value, :]=[1,1,1,1,1]
        nosieve=np.ones((Parameters.NumColors, 5), int)
        nosieve[value, :]=[0,0,0,0,0]

        for card in Players[receiver].cards:
            if Deck[card][0]==value:
                PosColors.append(card)
                ColorPunch[card]*=yessieve
                emptyclue=False
            else:
                ColorPunch[card]*=nosieve
    if type==1:
        yessieve=np.zeros((Parameters.NumColors, 5), int)
        yessieve[value, :]=[1,1,1,1,1]
        nosieve=np.ones((Parameters.NumColors, 5), int)
        nosieve[value, :]=[0,0,0,0,0]

        for card in Players[receiver].cards:
            if Deck[card][1]==value:
                PosNumbers.append(card)
                NumberPunch[card]*=yessieve
                emptyclue=False
            else:
                NumberPunch[card]*=nosieve
    if emptyclue and Parameters.ForbidEmptyClue:                                         #IF not ForbidEmptyClue, THIS ERROR SHOULD NEVER BE RAISED
        return("ERROR: CLUE MUST BE POSITIVE :)")
    return(None)

def Discard(player, card):
    #global Actions, Tokens, TopDeck
    if GameState.Tokens==Parameters.NumTokens and Parameters.MaxTokens:
        return("ERROR: CANNOT DISCARD WITH MAX NUMBER TOKENS")
    if card not in Players[player].cards:
        #print("Players[player].cards is ", Players[player].cards)
        #print("truth statement card in Players[player].cards", card in Players[player].cards)
        return("ERROR: CAN ONLY DISCARD FROM OWN HAND")
    PublicInfo.Actions.append(1)
    Players[player].cards.remove(card)
    Players[player].cards.append(GameState.TopDeck)
    PublicInfo.Discards.append(card)
    GameState.Tokens+=1
    GameState.TopDeck+=1
    if card in PosColors: PosColors.remove(card)
    if card in PosNumbers: PosNumbers.remove(card)
    return(None)

def Play(player, card):
    #global Actions, TopDeck, Fuses, Points
    if card not in Players[player].cards:
        return("ERROR: CAN ONLY PLAY CARDS FROM OWN HAND")
    PublicInfo.Actions.append(2)
    Players[player].cards.remove(card)
    Players[player].cards.append(GameState.TopDeck)
    GameState.TopDeck+=1
    if PublicInfo.Stacks[Deck[card][0]]==Deck[card][1]:
        GameState.Points+=1
        PublicInfo.Stacks[Deck[card][0]]+=1
        if card in PosColors: PosColors.remove(card)
        if card in PosNumbers: PosNumbers.remove(card)
        PublicInfo.TopStacks[Deck[card][0]]=card
        if sum(PublicInfo.Stacks)==Parameters.NumDistinctCards:
            return("GAME OVER! YOU SCORED {0} POINTS".format(sum(GameState.Stacks)))
    else:
        GameState.Fuses-=1
        PublicInfo.Discards.append(card)
        if GameState.Fuses==0:
            return("GAME OVER! LAST FUSE BLOWN!")
    return(None)

def ManualTakeAction(currentplayer):
    result=""
    action = input("Player {0} to play: ".format(currentplayer+1))
    action=action.split(" ")
    if action[0].lower()=="clue":
        if action[2].isalpha():
            result+="Cluing Player {0} about {1} {2}".format(action[1], 'color', action[2])
            clue=Clue(currentplayer, int(action[1])-1, 0, StrToNum.get(action[2].lower(), "enter color r, y, g, b, w, m"))
            if clue is not None:
                return(result+clue)
        elif action[2].isnumeric():
            result+="Cluing Player {0} about {1} {2}".format(action[1], 'number', action[2])
            clue=Clue(currentplayer, int(action[1])-1, 1, int(action[2])-1)
            if clue is not None:
                return(result+clue)
        else:
            return("INVALID CLUE")
    elif action[0].lower()=="discard" and action[1].isnumeric():
        return(Discard(currentplayer, int(action[1])))
    elif action[0].lower()=='play' and action[1].isnumeric():
        return(Play(currentplayer, int(action[1])))
    else:
        return("INVALID PLAY")