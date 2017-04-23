import math


def CalculateMarketValue(buyouts):
    MIN_PERCENTILE = 0.15
    MAX_PERCENTILE = 0.30
    MAX_JUMP = 1.2
    totalNum = 0
    totalBuyout = 0
    numRecords = len(buyouts)
    for i in range(0,numRecords):
        totalNum = i
        if i != 0 and i+1 > numRecords*MIN_PERCENTILE and (i+1>numRecords*MAX_PERCENTILE or buyouts[i]>= MAX_JUMP*buyouts[i-1]):
            break
        totalBuyout = totalBuyout + buyouts[i]
        if i+1 == numRecords :
            totalNum = i+1

    uncorrectedMean = totalBuyout/totalNum
    varience = 0
    for i in range(0,totalNum):
        varience = varience + (buyouts[i]-uncorrectedMean)**2

    stdDev = math.sqrt(varience/totalNum)
    correctedTotalBuyout = uncorrectedMean
    correctedTotalNum = 1
    for i in range(0, totalNum):

        if math.fabs(uncorrectedMean - buyouts[i]) < 1.5*stdDev:
            correctedTotalNum = correctedTotalNum + 1
            correctedTotalBuyout = correctedTotalBuyout + buyouts[i]

    correctedMeam = int(math.floor(correctedTotalBuyout/correctedTotalNum+0.5))

    return correctedMeam
def Data_Time(time,period_day):
    result_time = math.floor(time - period_day*60*60*24)
    return int(result_time)