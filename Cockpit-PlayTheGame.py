import copy, numpy as np

from Chassis import *



##############DEFAULTS##############
AutoPlay = False
Numbers=(1,1,1,2,2,3,3,4,4,5)
#MaxNum=max(Numbers)                    #GENERALIZE TO OTHER SETS OF Numbers (NOT READY YET)   
Colors=('r','y','g','b','w')           #POSSIBLY ADD SIXTH COLOR ... "m" FOR RAINBOW
NumColors=len(Colors)
NumPlayers=5
NumCards=4
NumTokens = 8
NumFuses = 3
ForbidEmptyClue = True                       #SET ForbidEmptyClue=True IF CLUES MUST GIVE SOME POSITIVE INFORMATION
####################################

PosNumbers.append(1)
PosColors.append(1)
PrintHands()

""" CurrentPlayer=0
Move=0

def TakeAction(currentplayer, blinded):
    if not AutoPlay:
        action = input("Take Action: ")
        action.split()
        if action[0].lower()=='clue':
            Clue(tuple([currentplayer]+action[1:4]))
        elif action[0].lower()=='discard':
            Discard(currentplayer)
        elif action[0].lower()=='play':
            print('wait for it')
 """

#    for number in Numbers:
#        for receiver in range(NumPlayers):
#            TakeAction(receiver, blinded.append(receiver))




""" 
LastRound=False
EndPlayer=-1
while not LastRound or CurrentPlayer!=EndPlayer:
    if TopDeck==len(Deck):
        LastRound=True
        TopDeck+=1                                      #ENSURES THIS BLOCK IS EXECUTED EXACTLY ONCE
        EndPlayer=CurrentPlayer
    print("breakpoint 1")
    PrintHands()
    TakeAction(CurrentPlayer, [CurrentPlayer])
    Move+=1
    CurrentPlayer=(CurrentPlayer+1)%NumPlayers """