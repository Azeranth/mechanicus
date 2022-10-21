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
    
    def __str__(self):
        bpoutput = BlueprintOutput.objects.filter(blueprint=self.blueprint)
        try:
            if bpoutput.count():
                item = bpoutput[0].item
            else:
                item = Item.objects.get(item_id=self.blueprint.blueprint_id)
        except:
            return 'invalid'
        return f'{self.quantity} {item.name} ({self.id})'
    
    def createChildJobs(self):
        inputs = BlueprintInput.objects.filter(blueprint=self.blueprint)
        for _input in inputs:
            _inputOutputs = BlueprintOutput.objects.filter(item=_input.item)
            for _inputOutput in _inputOutputs:
                requiredQuantity = self.quantity * _input.quantity
                runs = requiredQuantity / _inputOutput.quantity
                if requiredQuantity % _inputOutput.quantity:
                    runs+=1
                childJob = Job(creator=self.creator, assigner=self.assigner, assignee=None, parent=self, root=self.root, blueprint=_inputOutput.blueprint, quantity=runs)
                childJob.save()
                childJob.createChildJobs()
    
    def assignChildJobs(self, assignee, assigner):
        children = Job.objects.filter(parent=self).exclude(id=self.id)
        for child in children:
            child.assignee = assignee
            child.assigner = assigner
            child.save()
            child.assignChildJobs(assignee, assigner)
            
    def unassignChildJobs(self, assigner):
        children = Job.objects.filter(parent=self).exclude(id=self.id)
        for child in children:
            child.assignee = None
            child.assigner = assigner
            child.save()
            child.unassignChildJobs(assigner)
    
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank = False, null = True, related_name="job_creator_set")
    assigner = models.ForeignKey(User, on_delete=models.SET_NULL, blank = True, null = True, default=get_mechanicus_service_user, related_name="job_assigner_set")
    assignee = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, blank = True, null = True, related_name="job_assignee_set")
    parent = models.ForeignKey("Job", on_delete=models.CASCADE, default=None, blank = True, null = True, related_name="job_parent_set")
    root = models.ForeignKey("Job", on_delete=models.CASCADE, default=None, blank = True, null = True, related_name="job_root_set")
    blueprint = models.ForeignKey("Blueprint", on_delete=models.RESTRICT, blank = False, null = False)
    quantity = models.IntegerField(blank = False, null = False, default = 0)
    
class Blueprint(models.Model):
    blueprint_id = models.IntegerField(unique=True, blank = False, null = False)

class Item(models.Model):
    item_id = models.IntegerField(unique=True, blank = False, null = False)
    name = models.CharField(max_length = 128, blank = False, null = False)

class Skill(models.Model):
    skill_id = models.IntegerField(blank = False, null = False)
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