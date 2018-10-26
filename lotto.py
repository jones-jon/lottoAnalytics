import random
import json
import collections

# a start of some things I want to study
simulationData = {
    "totalNumberOfSimulations": 0,
    "lowSum": 0,  # sum of 174 and below
    "highSum": 0, #sum of 175 and above
    "pastWinningNumbersMatched": 0,
    "doublesPickedByAi": 0,
    "storage": {
        "rawNumbersPickedByAi": [],
        "rawSums": [],
        "numbersData": []
    },
    "analysis": {
        "sums": [],
        "numbers": [],
        "doubles": []
    },
    "cache": []
}

# gather the past winnings document
# this file is downloaded to avoid 
# need for internet connectivity
# data.gov website can be found here
# https://data.ny.gov/api/views/5xaw-6ayf/rows.json?accessType=DOWNLOAD
# download new versions after drawings
# to keep up to date
def getPastHistory():

    with open ("data/powerball/history.json") as p:
        pow = json.load(p)
    
    with open ("data/megamillions/history.json") as m:
        meg = json.load(m)
    
    return {
        "powerball": pow,
        "megamillions": meg
    }

def getWorkableData():
    files = getPastHistory()
    rawData = {
        "sumOfAList": [],
        "pastWins": [],
        "counters": {
            "sumCounter": []
        }
    }

    for m in files["megamillions"]["data"]:
        # They organize the numbers separately
        # The Powerball does not do this, something to look at if you use powerball list
        winningNumbers = m[9] #["1, 2, 3, 4, 5"]
        megaBall = m[10] # ["1"]

        # combine the two numbers, you can skip this step with powerball
        combineNumbersIntoOne = winningNumbers + " " + megaBall

        # split them up into separate segmaents
        # so we can work as a list
        arrayOfNumbers = combineNumbersIntoOne.split(" ")

        # this will build them into a list as integers: [1, 2, 3, 4, 5, megaball ]
        # we do this so we can work easier with math
        rawNumbersInList = [int(i) for i in arrayOfNumbers]
        
        # add the data to a json object
        rawData["pastWins"].append(rawNumbersInList)
        
        # since we built them into integers
        # we can now do some math wizardry and add them all up
        rawData["sumOfAList"].append(sum(rawNumbersInList))

    for x in files["powerball"]["data"]:
        # They organize the numbers separately
        # The Powerball does not do this, something to look at if you use powerball list

        winningNumbers = x[9]  # ["1, 2, 3, 4, 5, 6"]

        # split them up into separate segmaents
        # so we can work as a list
        arrayOfNumbers = winningNumbers.split(" ")

        # this will build them into a list as integers: [1, 2, 3, 4, 5, megaball ]
        # we do this so we can work easier with math
        rawNumbersInList = [int(i) for i in arrayOfNumbers]

        # add the data to a json object
        rawData["pastWins"].append(rawNumbersInList)

        # since we built them into integers
        # we can now do some math wizardry and add them all up
        rawData["sumOfAList"].append(sum(rawNumbersInList))

    # now since we gathered the sum of the lists
    # we can start doing some fun things
    # like seeing what sum of numbers gets drawn the most
    # Counter is pulled from collections and must be imported
    rawData["counters"]["sumCounter"] = collections.Counter(rawData["sumOfAList"])
    rawData["lastWin"] = rawNumbersInList

    return rawData

class NumbersGenerator:
    def __init__(self, mainNumbersRangeList, megaBallRangeList, sumRangeList, exclude, numberOfPicksInDraw, iterations, compareToLastWin):
        self.mainRange = mainNumbersRangeList
        self.megaRange = megaBallRangeList
        self.sumRange = sumRangeList
        self.exclude = exclude
        self.numberOfPicks = numberOfPicksInDraw
        self.iterations = iterations
        self.compareToLastWin = compareToLastWin
    
    def build(self):

        pastWinCheck = self.checkForLastNumberWinner()
        
        for x in range(self.iterations):
            currentDraw = self.checkNumbersThroughPast()
            simulationData["storage"]["rawNumbersPickedByAi"].append(currentDraw["numbers"])
            simulationData["storage"]["rawSums"].append(sum(currentDraw["numbers"]))
            simulationData["storage"]["numbersData"].append(currentDraw)
            print(x + 1) # so people dont freak out with the number count
            simulationData["totalNumberOfSimulations"] = x + 1
            
            if self.compareToLastWin:
                print(pastWinCheck)
            print("Ai pick: %s [%s]" % (currentDraw["numbers"], currentDraw["sum"]))
            print("*" * 100 + "//")
            
            if currentDraw["sum"] <= 174:
                simulationData["lowSum"] += 1
            
            if currentDraw["sum"] >= 175:
                simulationData["highSum"] += 1
            
            if pastWinCheck == currentDraw["numbers"] and self.compareToLastWin:
                print("+" * 400)
                print("The AI system picked the last winner")
                break 
                
        return

    def generate(self):
        dup = False
        numbersList = []
        for x in range(self.numberOfPicks):

            randomNumberGen = random.randint(self.mainRange["low"], self.mainRange["high"])

            # make sure only 1 of each number is drawn
            if randomNumberGen in numbersList:
                dup = True
                # generate a new number
                while dup:
                    randomNumberGen = random.randint(self.mainRange["low"], self.mainRange["high"])
                    if randomNumberGen not in numbersList:
                        numbersList.append(randomNumberGen)
                        dup = False
                continue
        
            numbersList.append(randomNumberGen)

        # sort the numbers from low to high for
        # easy reading
        finalNumbers = sorted(numbersList)
        
        # now we generate the mega ball
        finalNumbers.append(random.randint(self.megaRange["low"], self.megaRange["high"]))
        
        return finalNumbers

    def checkNumbersThroughPast(self):
        iterate = True
        pastWins = getWorkableData()["pastWins"]
        
        while iterate:
            ticket = self.generate()
            sumOfTicket = sum(ticket)
            
            if ticket in simulationData["storage"]["rawNumbersPickedByAi"]:
                simulationData["doublesPickedByAi"] += 1
                simulationData["analysis"]["doubles"].append(ticket)
            
            if self.sumRange["low"] <= sumOfTicket <= self.sumRange["high"]:
                if ticket not in pastWins:
                    if ticket not in simulationData["storage"]["rawNumbersPickedByAi"]:
                        iterate = False
                    else:
                        iterate = True
                else:
                    print("A past winner was chosen. Purchasing a different ticket")
                    simulationData["pastWinningNumbersMatched"] += 1
                    iterate = True
            else:
                iterate = True
        
        return {
            "numbers": ticket,
            "sum": sumOfTicket
        }
    
    def checkForLastNumberWinner(self):
        lastwinningNumbers = getWorkableData()["lastWin"]

        return "Last winner: %s [%s]" % (lastwinningNumbers, sum(lastwinningNumbers))
    
    def dataAnalysis(self):
        simulationData["analysis"]["numbers"] = collections.Counter(self.flattenNumbers(simulationData["storage"]["rawNumbersPickedByAi"]))
        
        del simulationData["storage"]["rawNumbersPickedByAi"]
        del simulationData["storage"]["numbersData"]
        simulationData["analysis"]["sums"] = collections.Counter(simulationData["storage"]["rawSums"])
        del simulationData["storage"]["rawSums"]
        print(simulationData)
        return
    
    def flattenNumbers(self, l):
        # remove the last number
        # because its a different range
        l.pop()
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, str):
                for sub in self.flattenNumbers(el):
                    yield sub
            else:
                yield el
# get the generator ready for build
# numbers will run through a filter
# if a filter is hit you will be notified
# with a printed message and it will regenerate
# to fulfill the request
getNumbers = NumbersGenerator(
    mainNumbersRangeList = {
        "low": 1,
        "high": 70
    },
    megaBallRangeList = {
        "low": 1,
        "high": 25
    },
    sumRangeList = {
        "low": 1,
        "high": 350
    },
    exclude = [],
    numberOfPicksInDraw = 5, 
    iterations = 125,
    compareToLastWin = False # this will show the last winning numbers and check for a winner
)

getNumbers.build()
getNumbers.dataAnalysis()
