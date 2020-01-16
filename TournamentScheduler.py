import copy
import time
from multiprocessing import Process, Queue

OUTPUT_FREQUENCY = 100000 # how often program will output when output code is uncommented
n = 20 # teams
k = 4 # number of games
d = 2 # difficulty increase
THREAD_INCREASE = 1
tracker = 0

def isValid(col, val, values, row):
    ##Checks if the team has already been scheduled to play against this opponent or a team of higher rank
    for i in values[row]: # Probably Removable
        if i >= val:
            return False
    return True

#Checks that the team's k games equal the weight that they should
def equalsWeight(values, row, q):
    addUp = 0
    for value in values[row][1:]:
        addUp += value
    weight = d * (row + 1) + ((k - d)*(n + 1)) / 2.0

    #Tracker is to show that the program is still running
    global tracker
    tracker += 1

    #Uncomment if you want to display where the program is currently searching
    #if tracker % OUTPUT_FREQUENCY == 0:
        #global solutions
        #print("number of solutions: " + str(q.qsize()) + " " + str(values) + "\n")
        #tracker = 0

    if addUp != weight:
        return False
    return True


#Checks if the values currently in use make it impossible to hit the correct weight for the team
def isOverWeight(values, row, col, val):
    addUp = val
    for value in values[row][1:col+1]:
        addUp += value
    weight = (d * (row + 1) + (((k - d)*(n + 1)) / 2))
    if addUp >= weight and col < k:
        return True
    if addUp > weight and col == k:
        return True
    return False

#Checks highest possible weight if this game is added
def opponentIsValid(games, team):
    addUp = sum(games[1:]) + games.count(-1)
    weight = (d * team + (((k - d) * (n + 1)) / 2))
    weightLowEnd = weight - (n * games.count(-1) - sum(range(1, games.count(-1))))

    if addUp >= weightLowEnd:
        return True
    return False


#Recursive function to check every game slot and try every opponent at each slot.
def getValue(row, values, col, start, end, q):
    if values[0][1] >= end:
        return False
    #Check if all teams are finished
    if row >= n:
        print ("Solution Found: " + str(q.qsize()) + " " + str(values) + "\n")
        return values
    #Check if finished with this team
    if col > k:
        if equalsWeight(values, row, q):
            return getValue(row + 1, values, 1, start, end, q)
        return False
    #Check if already has an opponent
    if values[row][col] != -1:
        solution = copy.deepcopy(getValue(row, values, col + 1, start, end, q))
        if solution != False:
            q.put(solution)
    else:
        #Probably a better way to do this rather then split into two similar branches
        #Only does from start to end on the first match
        if row == 0 and col == 1:
            for i in range(start, end + 1):
                if isOverWeight(values, row, col, i):
                    return False
                if -1 in values[i - 1] and isValid(col, i, values, row):
                    values[row][col] = i
                    values[i - 1][values[i - 1].index(-1)] = row + 1
                    solution = copy.deepcopy(getValue(row, values, col + 1, start, end, q))
                    if solution != False:
                        q.put(solution)
                        print ("Solution Found: " + str(q.qsize()) + " " + str(values) + "\n")
                        # return False
                    values[row][col] = -1
                    values[i - 1][values[i - 1].index(row + 1)] = -1
        #Checks all possible matches for any match after the first
        else:
            for i in range(row+1, n+1):
                if isOverWeight(values, row, col, i):
                    return False
                if -1 in values[i - 1] and isValid(col, i, values, row):
                    values[row][col] = i
                    values[i-1][values[i-1].index(-1)] = row+1
                    if opponentIsValid(values[i-1], i):
                        solution = copy.deepcopy(getValue(row, values, col + 1, start, end, q))
                        if solution != False:
                            q.put(solution)
                            print ("Solution Found: " + str(q.qsize()) + " " + values + "\n")
                    values[row][col] = -1
                    values[i - 1][values[i - 1].index(row+1)] = -1
    return False


def solve(start, end, q):
    values = []
    for x in range(1, n + 1):
        col = []
        col.append(x)
        for y in range(1, k + 1):
            col.append(-1)
        values.append(col)

    getValue(0, values, 1, start, end, q)
    global solutions
    if q.qsize() > 0:
        return True
    print ("No Solution " + str(start) + " - " + str(end) + "\n")
    return False

if __name__ == "__main__":
    start_time = time.time()
    solutions = Queue()

    #multiple threads each checking a range for the first team to play
    p1 = Process(target=solve, args=(2, 2+THREAD_INCREASE, solutions, ))
    p2 = Process(target=solve, args=(2+THREAD_INCREASE, 2 + THREAD_INCREASE * 2, solutions, ))
    p3 = Process(target=solve, args=(2 + THREAD_INCREASE * 2, 2 + THREAD_INCREASE * 3, solutions,))
    p4 = Process(target=solve, args=(2 + THREAD_INCREASE * 3, n, solutions,))
    #solve(1, n)

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p1.join()
    p2.join()
    p3.join()
    p4.join()


    #output all found solutions
    if solutions.qsize() > 0:
        s = "Solution: " + str(n) + " " + str(k) + " " + str(d) + " " + str(solutions.qsize()) + "\n"
        for i in range(solutions.qsize()):
            print(solutions.get())

        print(s)
    else:
        print("No Solutions")

    print("Time So Far: %s seconds" % (time.time() - start_time))

    print("--- %s seconds ---" % (time.time() - start_time))
