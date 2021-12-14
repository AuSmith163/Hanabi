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
    Colors=('r','o','y','g','b')                #POSSIBLY ADD 'm' FOR THE MULTICOLOR SET
    NumColors=len(Colors)
    NumPlayers=5
    NumCards=4                                  #NUMBER OF CARDS PER HAND
    NumTokens = 8
    MaxTokens = False                           #IF NumTokens IS THE MAXIMUM NUMBER OF POSSIBLE Tokens
    NumFuses = 3
    AutoPlay=[]                                 #COMPUTER PLAYERS
    ForbidEmptyClue = True                      #ForbidEmptyClue==True IF CLUES MUST GIVE SOME POSITIVE INFORMATION
    NumDistinctCards = NumColors*MaxNum         #TOTAL NUMBER OF CARDS
    SerialTieBreak = True                       #PLAYERS AGREE TO BREAK DISCARD/PLAY TIES BY LOWEST/HIGHEST SERIAL NUMBER
Parm=Parameters


##REALTIME VARIABLES

class PublicInfo:
    PosColors = []                                                                                           #CARDS THAT HAVE BEEN CLUED POSITVE COLOR
    PosNumbers = []                                                                                          #CARDS THAT HAVE BEEN CLUED POSITIVE NUMBER

    #CClues = []                                                         #MOVE NUMBER OF COLOR CLUES ----- INCLUDED IN Actions --- DEPRECATE?
    #ActiveCClues = []                                                  #JUST USE CClues AND NClues COMBINED WITH ActiveCards
    #NClues = []                                                         #MOVE NUMBER OF NUMBER CLUES ----- INCLUDED IN Actions --- DEPRECATE?
    #ActiveCards=np.reshape(range(Parm.NumPlayers*Parm.NumCards), (Parm.NumPlayers, Parm.NumCards))
    #ActiveNClues = []
    Trash = np.zeros((Parm.NumColors, 5), int)                                            #MATRIX COUNTING HOW MANY DISCARDS OF EACH COPY
    Discards = []
    Stacks=[0 for i in range(Parm.NumColors)]
    TopStacks=[i - Parm.NumColors for i in range(Parm.NumColors)]                   #DUMMY 0 CARDS AT END OF DECK FOR PRINTING
    StacksArray = np.zeros((Parm.NumColors, 5), int)                   #OUT STACKS BEFORE 1 IS PLAYED
    PlayNext=np.asarray([[1,0,0,0,0] for i in range(Parm.NumColors)])                   #MATRIX WITH 0 FOR SAFE AND 1 FOR ENDANGERED
    Endangered=np.zeros((Parm.NumColors, 5), int)
    #Extras = [[2,1,1,1,0] for i in range(Parm.NumColors)]          #ARRAY Numbers-Ones
    #LifeSpan=[(0,0) for i in range(len(Deck))]                          #MAYBE ONLY TRACK DEAD DATES OR NOT AT ALL, REPLACE TRASH HISTORY?
    Punch = {}                                                 #BINARY MATRICES FOR EACH CARD DETAILING ITS PUBLIC INFORMATION

    #HistoryActiveCards = [copy.deepcopy(ActiveCards)]
    #HistoryCClues = [[]]
    #HistoryNClues = [[]]
    #HistoryTrash = [copy.deepcopy(Trash)]

    Actions = []                                                         #LIST ACTION TYPE FOR EVERY MOVE ACCORDING TO 0: CLUE; 1: DISCARD; 2: PLAY
PI=PublicInfo

class GameState:
    TopDeck = Parm.NumPlayers*Parm.NumCards                                #TOP CARD AFTER THE DEAL
    Tokens = Parm.NumTokens                                        #INITIAL TOKENS
    Fuses = Parm.NumFuses                                          #INITIAL FUSES
    Points = 0
    Move = 0
    FinalRound = False
GS=GameState

class Player:
    def __init__(self):
        self.numcards=Parm.NumCards
        self.cards=[]
        self.DiscardOrder=[]
        self.info={}
        self.Endangered=[]
        self._Beliefs = {}                                                       #KEY=card               VALUE IS MATRIX OF HOW Player SEES THE BELIEFS OF THE PLAYER HOLDING card
        self._MetaBeliefs = {}                                                   #KEY=(card, PLAYER)     VALUE IS MATRIX OF WHAT Player BELIEVES ABOUT PLAYER'S Beliefs
    #def update():   

#CREATE AN ARRAY OF NumPlayers MANY HANDS, ONE ON EACH ROW WITH CARDS REPRESENTED BY SERIAL NUMBERS FROM
#THE ORIGINAL DECK, TOP TO BOTTOM, STARTING AT 0. WE DEAL EACH HAND FROM THE TOP OF THE DECK.
#CREATE A FULL SHUFFLED DECK WITH NOMENCLATURE AS IN (0,2) FOR "COLOR 0 AND NUMBER 2+1" OR JUST "red 3"
#THINK OF THE INDICES IN Deck AS SERIAL NUMBERS WRITTEN ON THE BACKS OF THE CARDS.

def CreateDeck():
    deck=[]
    for color in range(Parm.NumColors):
        for number in Parm.Numbers:
            deck.append((color,number-1))    #INTERNAL FORMAT COLORS AS INTEGERS (CONVERT USING StrToNum)
    shuffle(deck)
    return deck

Deck=tuple(CreateDeck()+[(i, -1) for i in range(Parm.NumColors)])

#ActiveCards = np.reshape(range(Parm.NumPlayers*Parm.NumCards),(Parm.NumPlayers, Parm.NumCards))
#ColorPunch = dict.fromkeys(range(len(Deck)), np.ones((Parm.NumColors, 5), int))
#NumberPunch = dict.fromkeys(range(len(Deck)), np.ones((Parm.NumColors, 5), int))                   #key=card (serial), value = PUBLIC CARD INFO BINARY MATRIX = 1 IF POSSIBLE, 0 IF IMPOSSIBLE

Players=[]

for i in range(Parm.NumPlayers):
    NewPlayer=Player()
    NewPlayer.cards=[*range(Parm.NumCards*i,Parm.NumCards*(i+1))]
    Players.append(NewPlayer)

for player in range(Parm.NumPlayers):
    for card in Players[player].cards:
        if Deck[card][1]==4:
            Players[player].Endangered.append(card)
            #print(Players[player].Endangered)

####################################################################################################
#######################################METADATA#####################################################
####################################################################################################
def OrderHand(player, subset, preferclued):
    result=[]
    for card in player.cards:
        if card in PI.Punch:
            continue
        PI.Punch[card]=np.ones((Parm.NumColors,5), int)
    #print("Punch", PI.Punch)
    probs=[1-np.sum(np.multiply(PI.Punch[player.cards[i]], subset))/np.sum(PI.Punch[player.cards[i]]) for i in range(Parm.NumCards)]
    #print("probs ", probs)
    args=list(np.argsort(probs))
    #print("argsort", args)
    #print("np.multiply(PI.Punch[player.cards[0]], PI.StacksArray)", np.multiply(PI.Punch[player.cards[0]], subset))
    #print("sums", np.sum(np.multiply(PI.Punch[player.cards[0]], subset)), np.sum(PI.Punch[player.cards[0]]))
    for arg in args:
        if probs[arg]==0:
            result.append(player.cards[arg])
    for arg in [x for x in args if probs[x]!=0 and probs[x]<1]:
        if (player.cards[arg] in PI.PosNumbers+PI.PosColors)==preferclued and probs[arg]<1:
            result.append(player.cards[arg])
    for arg in [x for x in args if probs[x]!=0 and probs[x]<1]:
        print("player.cards[arg] not in PI.PosNumbers.keys()", player.cards[arg], PI.PosNumbers)
        if (player.cards[arg] in PI.PosNumbers+PI.PosColors)!=preferclued:
            print("PosNumbers, PosColors, union", PI.PosNumbers, PI.PosColors, PI.PosNumbers+PI.PosColors)
            result.append(player.cards[arg])
    for arg in args:
        if probs[arg]==1:
            result.append(player.cards[arg])
    return(result)

####################################################################################################
########################################DISPLAY#####################################################
####################################################################################################


def DispCard(card, blinded=False):
    color = Deck[card][0]
    result=Typo.BOLD
    if blinded and card not in PI.PosNumbers:
        number="X"
    else:
        number=str(Deck[card][1]+1)
    if not blinded or card in PI.PosColors:
        result+=NumToDisp[color]
    if card in PI.PosColors and not blinded:
        result+=Typo.UNDERLINE
    if card in PI.PosNumbers and not blinded:
        result+="#"
    else:
        result+=" "
    
    if not blinded or card in PI.PosColors:
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
    for player in range(Parm.NumPlayers):
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
    result+="SCORE: {0}  TOKENS: {1}  FUSES: {2}".format(sum(PI.Stacks), GS.Tokens, GS.Fuses)
    result+="       STACKS : "
    for color in range(Parm.NumColors): result+=DispCard(PI.TopStacks[color])
    result+="       DISCARDS:       "
    for card in PI.Discards: result+=DispCard(card)
    result+="\n"
    return(result)



####################################################################################################
#####################################PLAY OPTIONS###################################################
####################################################################################################



def Clue(sender, receiver, type, value):
    emptyclue = True
    if not GS.Tokens:
        return("ERROR: INSUFFICIENT TOKENS TO CLUE")
    if sender==receiver:
        return("ERROR: CANNOT CLUE SELF")
    GS.Tokens-=1
    PI.Actions.append(0)
    if type==0:
        yessieve=np.zeros((Parm.NumColors, 5), int)
        yessieve[value, :]=[1,1,1,1,1]
        nosieve=np.ones((Parm.NumColors, 5), int)
        nosieve[value, :]=[0,0,0,0,0]

        for card in Players[receiver].cards:
            if Deck[card][0]==value:
                PI.PosColors.append(card)
                emptyclue=False
                if card in PI.Punch:
                    PI.Punch[card]=np.multiply(PI.Punch[card],yessieve)
                else:
                    PI.Punch[card]=yessieve
            else:
                if card in PI.Punch:
                    PI.Punch[card]=np.multiply(PI.Punch[card],nosieve)
                else:
                    PI.Punch[card]=nosieve
    if type==1:
        yessieve=np.zeros((Parm.NumColors, 5), int)
        yessieve[:, value]=[1,1,1,1,1]
        nosieve=np.ones((Parm.NumColors, 5), int)
        nosieve[:, value]=[0,0,0,0,0]

        for card in Players[receiver].cards:
            if Deck[card][1]==value:
                PI.PosNumbers.append(card)
                emptyclue=False
                if card in PI.Punch:
                    PI.Punch[card]=np.multiply(PI.Punch[card],yessieve)
                else:
                    PI.Punch[card]=yessieve
            else:
                if card in PI.Punch:
                    PI.Punch[card]=np.multiply(PI.Punch[card],nosieve)
                else:
                    PI.Punch[card]=nosieve
    if emptyclue and Parm.ForbidEmptyClue:                                         #IF not ForbidEmptyClue, THIS ERROR SHOULD NEVER BE RAISED
        return("ERROR: CLUE MUST BE POSITIVE :)")
    return(None)

def Discard(player, card):
    if GS.Tokens==Parm.NumTokens and Parm.MaxTokens:
        return("ERROR: CANNOT DISCARD WITH MAX NUMBER TOKENS")
    if card not in Players[player].cards:
        #print("Players[player].cards is ", Players[player].cards)
        #print("truth statement card in Players[player].cards", card in Players[player].cards)
        return("ERROR: CAN ONLY DISCARD FROM OWN HAND")
    PI.Actions.append(1)
    Players[player].cards.remove(card)
    Players[player].cards.append(GS.TopDeck)
    PI.Discards.append(card)
    GS.Tokens+=1
    GS.TopDeck+=1
    if card in PI.PosColors: PI.PosColors.remove(card)
    if card in PI.PosNumbers: PI.PosNumbers.remove(card)
    return(None)

def Play(player, card):
    color=Deck[card][0]
    number=Deck[card][1]
    if card not in Players[player].cards:
        return("ERROR: CAN ONLY PLAY CARDS FROM OWN HAND")
    PI.Actions.append(2)
    Players[player].cards.remove(card)
    Players[player].cards.append(GS.TopDeck)
    GS.TopDeck+=1
    if PI.Stacks[color]==number:
        GS.Points+=1
        PI.Stacks[color]+=1
        PI.StacksArray[Deck[card]]=1
        PI.PlayNext[Deck[card]]=0
        if number<Parm.MaxNum:
            PI.PlayNext[color, number+1]=1
        if Deck[card][1]+1==Parm.MaxNum:
            GS.Tokens+=1
        if card in PI.PosColors: PI.PosColors.remove(card)
        if card in PI.PosNumbers: PI.PosNumbers.remove(card)
        PI.TopStacks[Deck[card][0]]=card
        if sum(PI.Stacks)==Parm.NumDistinctCards:
            return("GAME OVER! YOU SCORED {0} POINTS".format(sum(PI.Stacks)))
    else:
        GS.Fuses-=1
        PI.Discards.append(card)
        if card in PI.PosColors: PI.PosColors.remove(card)
        if card in PI.PosNumbers: PI.PosNumbers.remove(card)
        if GS.Fuses==0:
            return("GAME OVER! LAST FUSE BLOWN!")
    return(None)


def FullInfo(card):
    if card in PI.Punch:
        matrix=PI.Punch[card]
    else:
        matrix=np.ones((Parm.NumColors, 5), int)

    result="CARD #"+f"{card:02}"+"\n"
    for color in range(Parm.NumColors):
        result+="   "+NumToDisp[color]
        for number in range(Parm.MaxNum):
            if matrix[color, number]:
                result+="   {0}    ".format(number+1)
            else:
                result+="        "
        result+=Typo.RESET+"\n"
    return(result)

def CheatFind(col, num):
    result=[]
    for i in range(len(Deck)):
        print("Deck[i]==(col,num): ", col, num, Deck[i]==(col,num))
        if Deck[i][0]==int(col) and Deck[i][1]==int(num):
            result.append(i)
    return(result)


def ManualTakeAction(currentplayer):
    result=""
    action = input("PLAYER {0}'S TURN (clue_<receiver>_<value>/discard_<#>/play_<#>): ".format(currentplayer+1))
    action=action.split(" ")
    if action[0].lower()=="clue":
        if not action[1].isnumeric() or int(action[1])-1 not in range(Parm.NumPlayers):
            return("SECOND INPUT OF CLUE MUST BE RECEIVING PLAYER NUMBER")
        if action[2] in Parm.Colors:
            result+="Cluing Player {0} about {1} {2}".format(action[1], 'color', action[2])
            clue=Clue(currentplayer, int(action[1])-1, 0, StrToNum[action[2].lower()])
            if clue is not None:
                return(result+clue)
        elif action[2].isnumeric() and int(action[2])-1 in range(Parm.MaxNum):
            result+="Cluing Player {0} about {1} {2}".format(action[1], 'number', action[2])
            clue=Clue(currentplayer, int(action[1])-1, 1, int(action[2])-1)
            if clue is not None:
                return(result+clue)
        else:
            return("THIRD INPUT OF CLUE MUST BE {0} or {1}".format(Parm.Colors, tuple([1+i for i in range(Parm.MaxNum)])))
    elif action[0].lower()=="discard" and action[1].isnumeric():
        return(Discard(currentplayer, int(action[1])))
    elif action[0].lower()=="play" and action[1].isnumeric():
        return(Play(currentplayer, int(action[1])))
    elif action[0].lower()=="full":
        #result+="DISPLAYING FULL INFO\n"
        for card in action:
            if not card.isnumeric():
                continue
            full=FullInfo(int(card))
            if full is not None:
                result+=full
        return result
    elif action[0].lower()=="find":
        result+="CHEAT: Cards that match: "+str(CheatFind(action[1], action[2]))
        return(result)
    elif action[0].lower()=="dorder" and action[1].isnumeric():
        result+="DISCARD ORDER: "+str(OrderHand(Players[int(action[1])-1], PI.StacksArray, False))
        return(result)
    elif action[0].lower()=="porder" and action[1].isnumeric():
        result+="PLAY ORDER: "+str(OrderHand(Players[int(action[1])-1], PI.PlayNext, True))
        return(result)
    else:
        return("INVALID PLAY")