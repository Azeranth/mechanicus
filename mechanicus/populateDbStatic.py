from yaml import load, dump
from yaml import Loader, Dumper
from mechanicus.models import Job,Blueprint,Item,Skill,CharacterSkillMap,BlueprintOutput,BlueprintInput,BlueprintSkill
from esi.clients import EsiClientProvider
from django.db.utils import IntegrityError

print("Loading groups from disk...")
with open('/mnt/a/sde/sde/fsd/groupIDs.yaml') as inFile:
    groupData = load(inFile, Loader=Loader)

print("Groups loaded.")
print("Loading blueprints from disk... (This will take a while)")
with open('/mnt/a/sde/sde/fsd/blueprints.yaml') as inFile:
    bpData = load(inFile, Loader=Loader)

print("Blueprints loaded.")
print("Loading Items from disk... (This will take a while)")
with open('/mnt/a/sde/sde/fsd/typeIDs.yaml') as inFile:
    itemData = load(inFile, Loader=Loader)

print("Items loaded.")

print("Finding skill groups...")
skillGroups = [k for k in groupData if groupData[k]['categoryID'] == 16]
skillTypes = [k for k in itemData if itemData[k]['groupID'] in skillGroups]
print("Groups found.")

print("Creating Skill records...")
i=0
d=len(skillTypes)
for skill in skillTypes:
    for o in range(1,6):
        try:
            s = Skill(skill_id=skill, level=o, name=itemData[skill]['name']['en'])
        except:
            s = Skill(skill_id=skill, name='invalidSkill')
            print('invalid skill_id: ' + str(skill))
        try:
            s.save()
        except IntegrityError::
            pass
    i+=1
    print(str(round((i/d)*100,2)) + '%', end='\r', flush=True)

print('\n', end='')
print("Records created")

print("Finding all items referenced in all blueprints")
allItems = []
i=0
d=len(bpData)
for key in bpData:
    blueprint = bpData[key]
    mats = []
    prods = []
    try:
        mats = blueprint['activities']['manufacturing']['materials']
    except KeyError:
        pass
    for mat in mats:
        if not mat['typeID'] in allItems:
            allItems.append(mat['typeID'])
    try:
        prods = blueprint['activities']['manufacturing']['products']
    except KeyError:
        pass
    for prod in prods:
        if not prod['typeID'] in allItems:
            allItems.append(prod['typeID'])
    try:
        mats = blueprint['activities']['reaction']['materials']
    except KeyError:
        pass
    for mat in mats:
        if not mat['typeID'] in allItems:
            allItems.append(mat['typeID'])
    try:
        prods = blueprint['activities']['reaction']['products']
    except KeyError:
        pass
    for prod in prods:
        if not prod['typeID'] in allItems:
            allItems.append(prod['typeID'])
    i+=1
    print(str(round((i/d)*100,2)) + '%', end='\r', flush=True)

print('\n', end='')
print("Search complete")

print("Creating all item records")
i=0
d=len(allItems)
for item in allItems:
    try:
        it = Item(item_id=item, name=itemData[item]['name']['en'])
    except:
        it = Item(item_id=item, name='invalidItem')
        print('invalid item_id: ' + str(item))
    try:
        it.save()
    except IntegrityError:
        pass
    i+=1
    print(str(round((i/d)*100,2)) + '%', end='\r', flush=True)

print('\n', end='')
print("Records created")

print("Creating all blueprint item records")
i=0
d=len(bpData)
for item in bpData:
    try:
        it = Item(item_id=item, name=itemData[item]['name']['en'])
    except:
        it = Item(item_id=item, name='invalidItem')
        print('invalid item_id: ' + str(item))
    try:
        it.save()
    except IntegrityError::
        pass
    i+=1
    print(str(round((i/d)*100,2)) + '%', end='\r', flush=True)

print('\n', end='')
print("Records created")

print("Creating all blueprint input, output, and skill records")
i=0
d=len(list(bpData))
for key in bpData:
    bp = Blueprint(blueprint_id=key)
    try:
        bp.save()
    except IntegrityError:
        pass
    mats = []
    prods = []
    skills = []
    try:
        mats = bpData[key]['activities']['manufacturing']['materials']
    except KeyError:
        pass
    try:
        mats = bpData[key]['activities']['reaction']['materials']
    except KeyError:
        pass
    for mat in mats:
        try:
            bi = BlueprintInput(blueprint=bp, item=Item.objects.get(item_id=mat['typeID']), quantity=mat['quantity'])
            try:
                bi.save()
            except IntegrityError::
                pass
        except:
            print('missing item' + str(mat['typeID']))
    try:
        prods = bpData[key]['activities']['manufacturing']['products']
    except KeyError:
        pass
    try:
        prods = bpData[key]['activities']['reaction']['products']
    except KeyError:
        pass
    for prod in prods:
        try:
            bo = BlueprintOutput(blueprint=bp, item=Item.objects.get(item_id=prod['typeID']), quantity=prod['quantity'])
            try:
                bo.save()
            except IntegrityError::
                pass
        except:
            print('missing item' + str(prod['typeID']))
    try:
        skills = bpData[key]['activities']['manufacturing']['skills']
    except KeyError:
        pass
    try:
        skills = bpData[key]['activities']['reaction']['skills']
    except KeyError:
        pass
    for skill in skills:
        try:
            bs = BlueprintSkill(blueprint=bp, skill=Skill.objects.get(skill_id=skill['typeID'], level=skill['level'] if skill['level'] > 0 else 5))
            try:
                bs.save()
            except IntegrityError:
                pass
        except Exception as e:
            print(e)
            print(skill['typeID'])
            print(skill['level'])
            print('missing skill: ' + str(skill['typeID']))

    i+=1
    print(str(round((i/d)*100,2)) + '%', end='\r', flush=True)

print('\n', end='')
print("Records created")