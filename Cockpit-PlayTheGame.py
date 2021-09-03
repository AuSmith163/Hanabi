import copy, numpy as np

from Chassis import *

CurrentPlayer=0
LastRound=False                                                     #THE GAMES END COMES IN THE LAST ROUND JUST BEFORE
EndPlayer=-1                                                        #EndPlayer WOULD PLAY

while not LastRound or CurrentPlayer!=EndPlayer:
    if GameState.TopDeck==len(Deck):                                #JUST AFTER LAST CARD DRAWN
        LastRound=True
        GameState.TopDeck+=1                                        #ENSURES THIS BLOCK IS EXECUTED EXACTLY ONCE
        EndPlayer=CurrentPlayer
    if CurrentPlayer in Parameters.AutoPlay:
        print(Hands([CurrentPlayer]))
    #    AutoTakeAction([CurrentPlayer])                            #COMPUTER PLAYS
    else:
        print(Hands([CurrentPlayer]))
        result = ManualTakeAction(CurrentPlayer)                    #HUMAN PLAYS
        if result is not None:
            print(Typo.ONRED+result+Typo.RESET)                     #INCORRECT INPUT ERROR MESSAGE
            if result.startswith("GAME OVER"):
                print(Hands())
                break                                               #BREAKS OUT AT GAMES END
            continue
    GameState.Move+=1                                               #END OF MOVE INCREMENTS THE MOVE NUMBER
    CurrentPlayer=(CurrentPlayer+1)%Parameters.NumPlayers           #NEXT PLAYER TO PLAY