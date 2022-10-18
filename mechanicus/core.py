from django.core.exceptions import ObjectDoesNotExist
import sys

def isCanMakeItem(character, item):
    reqSkills = Skill.objects.filter(id__in=[bpskill.skill_id for bpskill in BlueprintSkill.objects.filter(blueprint_id=BlueprintOutput.objects.get(item_id=Item.objects.get(name=itemName).id).blueprint_id)])
	return reqSkills.count() == CharacterSkillMap.objects.filter(character_id=character, skill_id__in=reqSkills).count()

def isCanMakeItemByName(characterName, itemName):
	try:
		reqSkills = Skill.objects.filter(id__in=[bpskill.skill_id for bpskill in BlueprintSkill.objects.filter(blueprint_id=BlueprintOutput.objects.get(item_id=Item.objects.get(name=itemName).id).blueprint_id)])
	except ObjectDoesNotExist:
		print("Requested item '" + itemName +"' could not be found", file=sys.stderr)
		return False
	try:
		character = EveCharacter.objects.get(character_name = characterName)
	except ObjectDoesNotExist:
		print("Requested Character '" + characterName +"' could not be found", file=sys.stderr)
		return False
	return reqSkills.count() == CharacterSkillMap.objects.filter(character_id=character, skill_id__in=reqSkills).count()
    