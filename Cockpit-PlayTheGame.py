import copy, numpy as np

from Chassis import *

print("\n\nI AM FLOWER POWER, A HANABI BOT! SO FAR, I ONLY ALLOW HUMAN PLAYERS.\n\n")
print("TO GIVE A CLUE, TYPE 'clue<space><player><space><value>' WHERE value IS IN r,o,y,g,b,1,2,3,4,5\n")
print("TO PLAY OR DISCARD A CARD, TYPE 'play<space><serial>' or 'discard<space><serial>'\n")
print("TO SEE THE NEGATIVE INFORMATION ABOUT A CARD, TYPE 'full<space><serial>' \n\n")





#REDO! NEED COMPLETE DISCARD STRUCTURE

""" def GetAlarm(player, n):           #PASSING player OBJECT
    if player.DiscardOrder:        #CHECKING THAT EVERYONE AGREES ON DISCARD ORDER
        alarm=0
        while player.DiscardOrder[alarm]:
            alarm+=1
        return(alarm)

def AutoTakeAction(n, player):        #PASSING player OBJECT SO ONLY player'S PRIVATE INFO IS ACCESSED, assumed player=Players[n]
    alarms=[]
    ahead=1
    while True:
        if ahead==0:                 #player CANNOT KNOW HIS OWN ALARM
            break
        nextalarm=GetAlarm(Players[n+ahead])
        alarms.append(nextalarm)
        if nextalarm==0:
            break """








CurrentPlayer=0
LastRound=False                                                     #THE GAMES END COMES IN THE LAST ROUND JUST BEFORE
EndPlayer=None                                                        #EndPlayer WOULD PLAY
Triggered=False

while not LastRound or CurrentPlayer!=EndPlayer:
    if GS.TopDeck==Parm.NumColors*len(Parm.Numbers) and not Triggered:                                #JUST AFTER LAST CARD DRAWN
        LastRound=True
        Triggered=True                                        #ENSURES THIS BLOCK IS EXECUTED EXACTLY ONCE
        EndPlayer=CurrentPlayer
    if CurrentPlayer in Parm.AutoPlay:
        print(Hands([CurrentPlayer]))
    #    AutoTakeAction([CurrentPlayer])                            #COMPUTER PLAYS
    else:
        print(Hands([CurrentPlayer]))
        result = ManualTakeAction(CurrentPlayer)                    #HUMAN PLAYS
        if result is not None:
            if result.startswith("CARD"):
                print(result)
                continue
            print(Typo.ONRED+result+Typo.RESET)                     #INCORRECT INPUT ERROR MESSAGE
            if result.startswith("GAME OVER"):
                print(Hands())
                break                                               #BREAKS OUT AT GAMES END
            continue
    GS.Move+=1                                               #END OF MOVE INCREMENTS THE MOVE NUMBER
    CurrentPlayer=(CurrentPlayer+1)%Parm.NumPlayers           #NEXT PLAYER TO PLAY

if GS.Fuses>0:
    print(Hands())