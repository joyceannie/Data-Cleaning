import matplotlib.pyplot as plt
import numpy as np
import sys

inputFileFromCorpus='inp1_cleaning1_tiny.csv'

def getUserIdToRatings(fileName, maxInputLines):
    userIdToRatings = {}
    movieIdToRatings = {}
    lineNumber = 0    

    f = open(fileName)
    for line in f:
        lineNumber = lineNumber + 1
        if lineNumber < maxInputLines:
            try:
                movie_vector = line.split(",")
                movie_id = movie_vector[0]
                movie_ratings = movie_vector[1:]
                num_ratings_for_movie = 0
                tot_rating_for_movie = 0
                for movie_rating in movie_ratings:
                    user_rating = movie_rating.split("_")
                    user_id = int(user_rating[0])
                    rating = int(user_rating[1])
                    if userIdToRatings.has_key(user_id):
                        userIdToRatings[user_id][0] = userIdToRatings[user_id][0] + 1
                        userIdToRatings[user_id][1] = userIdToRatings[user_id][1] + rating
                    else:
                        userIdToRatings[user_id] = [1,rating]
                    num_ratings_for_movie = num_ratings_for_movie + 1
                    tot_rating_for_movie = tot_rating_for_movie + rating
            	if movieIdToRatings.has_key(movie_id):
                    print " ERROR : Movie  is alredy present in map, movieIdToRatings[", movie_id ,"] = ", movieIdToRatings[movie_id], " . Line#", lineNumber, " from file is " + line
            	elif tot_rating_for_movie == 0 or num_ratings_for_movie == 0:
	            print " Noisy data. tot_rating_for_movie = " , tot_rating_for_movie , " num_ratings_for_movie = " , num_ratings_for_movie , " . Line#", lineNumber, " from file is " + line
	    	else:
                    movieIdToRatings[movie_id] = [num_ratings_for_movie,tot_rating_for_movie]
    	    except:
                print "Unexpected error:", sys.exc_info()[0], " on lineNumber#", lineNumber, " - ", line
    print "lineNumber = " , lineNumber
    f.close()
    return userIdToRatings,movieIdToRatings

def getRatingInfo(userIdToRatings):
    ratings = []
    avgRatings = []
    for userId, ratingInfo in userIdToRatings.items():
        numRatings = ratingInfo[0]
        totRating = ratingInfo[1]
        avgRating = float(totRating)/numRatings
        ratings.append(numRatings)
        avgRatings.append(avgRating)
    return ratings,avgRatings

def getAvgRatingMap(userIdToRatings):
    userIdToAvgRating = {}
    avgRatings = []
    for userId, ratingInfo in userIdToRatings.items():
        numRatings = ratingInfo[0]
        totRating = ratingInfo[1]
        avgRating = float(totRating)/numRatings
        userIdToAvgRating[userId] = avgRating
    return userIdToAvgRating

def plotQuantile(distro1,col1,title):
    quantileRange = range(0,101,1)
    quantileValues1 = np.percentile(distro1, quantileRange)
    plt.plot(quantileRange,quantileValues1)
    leg = []
    leg.append("%s (%d)" %(col1, len(distro1)))
    plt.legend(leg)
    plt.title(title)
    plt.grid(True)
    plt.show()

#kmeansDataClean.plotQuantile(kmeansDataClean.numRatingsPerUser, 'numRatingsPerUser', 'Quantiles of Number of ratings per user')
#kmeansDataClean.plotQuantile(kmeansDataClean.numRatingsPerMovie, 'numRatingsPerMovie', 'Quantiles of Number of ratings for a movie')
#kmeansDataClean.plotQuantile(kmeansDataClean.avgRatingsPerUser, 'avgRatingsPerUser', 'Quantiles of avgRating given by a user')
#kmeansDataClean.plotQuantile(kmeansDataClean.avgRatingsPerMovie, 'avgRatingsPerMovie', 'Quantiles of avgRating for a movie')

#U = 480215
#M = 20000

def getInvertedIndexFromKey(userIdToRatings):
    userList = []
    errors = 0
    for u in userIdToRatings.iterkeys():
        try:
            userList.append(int(u))
        except:
            errors = errors + 1
    print "Invalid keys : " , errors
    keyIdx = 0
    invertedKeyIdx = {}
    for k in userList:
        invertedKeyIdx[k] = keyIdx
        keyIdx = keyIdx + 1
    return invertedKeyIdx

def generateKmeansDataSet(fileName,invertedIdx,avgRatingMap,startRow,endRow,outputFile):
    f = open(fileName)
    o = open(outputFile, "w")
    lineNumber = 0
    numUsers = len(invertedIdx)
    print "totalUsers = " , numUsers, " len(avgRatingMap) = ", len(avgRatingMap)
    for line in f:
        lineNumber = lineNumber + 1
        if lineNumber >= startRow and lineNumber <= endRow:
            try:
                movie_vector = line.split(",")
                movie_id = movie_vector[0]
                movie_ratings = movie_vector[1:]
                ratingVector = []
                for userId in range(0,numUsers):
                    ratingVector.append(-1.0)
                print len(ratingVector) , " => " , ratingVector 
                for origUserId,avgRating in avgRatingMap.iteritems():
                    userId = invertedIdx[origUserId]
                    ratingVector[userId] = avgRating
                print len(ratingVector) , " => " , ratingVector 
                for movie_rating in movie_ratings:
                    user_rating = movie_rating.split("_")
                    user_id = int(user_rating[0])
                    print user_id,user_rating
                    ratingVector[invertedIdx[user_id]] = user_rating
            except:
                print "Error in processing!! ", sys.exc_info()
            o.write(movie_id)
            for rating in ratingVector:
                o.write('\t')
                o.write("%d" % (rating))   
    	    o.write('\n')
    f.close()
    o.close()

def printInvertedIdxWithAvgRating(avgRatingMap,invertedIdx,invertedIdxFile):
    type(avgRatingMap)
    type(invertedIdx)
    numUsers = len(invertedIdx)
    numUsersInRatingMap = len(avgRatingMap)
    print "len(invertedIdx) = " , numUsers , " ,len(avgRatingMap) = ", numUsersInRatingMap
    errors = 0
    ctr = 0
    for origUserId, avgRating in avgRatingMap.iteritems():
        if invertedIdx.has_key(origUserId) is False:
            print "Error avgRatingMap.userId ", origUserId , "out of range"

    f = open(invertedIdxFile,"w")
    for origUserId, userId in invertedIdx.iteritems():
        if userId>=numUsersInRatingMap:
            print "Error userId ", userId , "out of range[0,", numUsers ,")"
        try:
            #if ctr < 20:
            #    print [origUserId, userId]
            #    ctr = ctr + 1
            avgRating =  avgRatingMap[int(origUserId)]
            f.write(origUserId)
            f.write('\t')
            f.write(userId)
            f.write('\t')
            f.write(avgRating)
            f.write('\n')
        except:
            errors = errors + 1
    print "errors = " , errors 
    f.close()

userIdToRatings,movieIdToRatings = getUserIdToRatings(inputFileFromCorpus, 21000)
numRatingsPerUser,avgRatingsPerUser = getRatingInfo(userIdToRatings)
numRatingsPerMovie,avgRatingsPerMovie = getRatingInfo(movieIdToRatings)

avgRatingMap=getAvgRatingMap(userIdToRatings)
invertedIdx=getInvertedIndexFromKey(userIdToRatings)
printInvertedIdxWithAvgRating(avgRatingMap,invertedIdx,"invertedUserIdx.csv")
#generateKmeansDataSet(inputFileFromCorpus,invertedIdx,avgRatingMap,1,100,'moviedataset_1.csv')
