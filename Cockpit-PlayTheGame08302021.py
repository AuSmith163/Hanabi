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




#    for number in Numbers:
#        for receiver in range(NumPlayers):
#            TakeAction(receiver, blinded.append(receiver))

CurrentPlayer=0
Move=0
LastRound=False
EndPlayer=-1

#def AutoTakeAction(currentplayer):
#    print("Auto Action....")

#while not LastRound or CurrentPlayer!=EndPlayer:
for k in range(5):
    try:
        if TopDeck==len(Deck):
            LastRound=True
            TopDeck+=1                                      #ENSURES THIS BLOCK IS EXECUTED EXACTLY ONCE
            EndPlayer=CurrentPlayer
        if AutoPlay:
            PrintHands(CurrentPlayer, False)
        #    AutoTakeAction(CurrentPlayer)
        else:
            PrintHands(CurrentPlayer)
            localres = ManualTakeAction(CurrentPlayer)
        Move+=1
        CurrentPlayer=(CurrentPlayer+1)%NumPlayers
    except ValueError as error:
        print(error)
    except Exception as error:
        print(error)
        break