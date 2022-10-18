from yaml import load, dump
from yaml import Loader, Dumper

with open('/mnt/a/sde/sde/fsd/blueprints.yaml') as inFile:
    bpData = load(inFile, Loader=Loader)

def getMaterialsByBlueprint(bpDict, blueprintId):
    try:
        return bpDict[blueprintId]['activities']['manufacturing']['materials']
    except KeyError:
        return []

def getMaterialsByProduct(bpDict, productId):
    return [getMaterialsByBlueprint(bpDict, blueprintId) for blueprintId in getBlueprintsByProduct(bpDict, productId)]

def getProductsByBlueprint(bpDict, blueprintId):
    try:
        return bpDict[blueprintId]['activities']['manufacturing']['products']
    except KeyError:
        return []

def getBlueprintsByProduct(bpDict, productId):
    rtn = []
    for key in bpDict:
        value = bpDict[key]
        try:
            products = value['activities']['manufacturing']['products']
        except KeyError:
            products = []
        for product in products:
            if product['typeID'] == productId:
                rtn.append(key)
    return rtn

def buildJobTree(bpDict, productId, quantity):
    rtn = [quantity, productId,[]]
    mats = getMaterialsByProduct(bpDict, productId)
    if mats:
        mats = mats[0]
    for mat in mats:
        rtn[2].append(buildJobTree(bpDict,mat['typeID'], quantity * mat['quantity']))
    return rtn

def getTabs(index):
    return "\t" * index

def RenderByTree(jobTree, index = 0):
    rtn = ""
    rtn += f'\n{getTabs(index)}{jobTree[0]} x {jobTree[1]}'
    for i in jobTree[2]:
        rtn += f'\n{getTabs(index + 1)}{RenderByTree(i, index + 1)}'
    return rtn

def getRawMaterialsByJobTree(jobTree):
    rtn = {}
    if jobTree[2]:
        for subJob in jobTree[2]:
            mats = getRawMaterialsByJobTree(subJob)
            for mat in mats:
                if mat in rtn:
                    rtn[mat] += mats[mat]
                else:
                    rtn.update({mat :mats[mat]})
    else:
        if jobTree[1] in rtn:
            jobTree[1] += jobTree[0]
        else:
            rtn.update({jobTree[1]:jobTree[0]})
    return rtn

def getJobsByJobTree(jobTree):
    rtn = {}
    if jobTree[2]:
        if jobTree[1] in rtn:
            jobTree[1] += jobTree[0]
        else:
            rtn.update({jobTree[1]:jobTree[0]})
        for subJob in jobTree[2]:
            jobs = getJobsByJobTree(subJob)
            if jobs:
                for job in jobs:
                    if job in rtn:
                        rtn[job] += jobs[job]
                    else:
                        rtn.update({job :jobs[job]})
    return rtn

