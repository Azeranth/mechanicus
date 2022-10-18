from django.db import models
from django.contrib.auth.models import User
from allianceauth.eveonline.models import EveCharacter

# Create your models here.


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),
            ("job_view_open_access","View access to open or unassigned jobs"),
            ("job_view_all_access","View access to all jobs"))
            
class Job(models.Model):
    def get_mechanicus_service_user():
        mechd = User.objects.get_or_create(username="mechanicusd")[0]
        if mechd.is_active:
            mechd.is_active = False
            mechd.save()
        return mechd

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank = False, null = True, related_name="job_creator_set")
    assigner = models.ForeignKey(User, on_delete=models.SET_NULL, blank = True, null = True, default=get_mechanicus_service_user, related_name="job_assigner_set")
    assignee = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, blank = True, null = True, related_name="job_assignee_set")
    parent = models.ForeignKey("Job", on_delete=models.CASCADE, default=None, blank = True, null = True, related_name="job_parent_set")
    root = models.ForeignKey("Job", on_delete=models.CASCADE, default=None, blank = True, null = True, related_name="job_root_set")
    product = models.ForeignKey("Blueprint", on_delete=models.RESTRICT, blank = False, null = True)
    
class Blueprint(models.Model):
    blueprintId = models.IntegerField(unique=True, blank = False, null = False)

class Item(models.Model):
    itemId = models.IntegerField(unique=True, blank = False, null = False)
    name = models.CharField(max_length = 128, blank = False, null = False)

class Skill(models.Model):
    skillId = models.IntegerField(blank = False, null = False)
    name = models.CharField(max_length = 128, blank = False, null = False)
    level = models.IntegerField(blank = False, null = False)

class CharacterSkillMap(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, blank = False, null = False)
    skill = models.ForeignKey("Skill", on_delete=models.CASCADE, blank = False, null = False)

class BlueprintOutput(models.Model):
    blueprint = models.ForeignKey("Blueprint", on_delete=models.CASCADE, blank = False, null = False)
    item = models.ForeignKey("Item", on_delete=models.CASCADE, blank = False, null = False)
    quantity = models.IntegerField(blank = False, null = False)

class BlueprintInput(models.Model):
    blueprint = models.ForeignKey("Blueprint", on_delete=models.CASCADE, blank = False, null = False)
    item = models.ForeignKey("Item", on_delete=models.CASCADE, blank = False, null = False)
    quantity = models.IntegerField(blank = False, null = False)

class BlueprintSkill(models.Model):
    blueprint = models.ForeignKey("Blueprint", on_delete=models.CASCADE, blank = False, null = False)
    skill = models.ForeignKey("Skill", on_delete=models.CASCADE, blank = False, null = False)