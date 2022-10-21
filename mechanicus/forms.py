from django.forms import ModelForm,IntegerField,BooleanField
from django.contrib.auth.models import User
from allianceauth.eveonline.models import EveCharacter

from .models import Job,Blueprint,Item,Skill,CharacterSkillMap,BlueprintOutput,BlueprintInput,BlueprintSkill

allBpsQueryset = Blueprint.objects.filter(id__in=[bpout.blueprint.id for bpout in BlueprintOutput.objects.all()])
allBpsLabelset = {bp: BlueprintOutput.objects.get(blueprint=bp).item.name for bp in allBpsQueryset}

CharSkillQuery = 'select eveonline_evecharacter.* from eveonline_evecharacter inner join mechanicus_characterskillmap on eveonline_evecharacter.id = mechanicus_characterskillmap.character_id inner join mechanicus_skill on mechanicus_skill.id = mechanicus_characterskillmap.skill_id inner join mechanicus_blueprintskill on mechanicus_blueprintskill.skill_id = mechanicus_skill.id where mechanicus_blueprintskill.blueprint_id = %s group by eveonline_evecharacter.id having count(*) = (select count(*) from mechanicus_skill inner join mechanicus_blueprintskill on mechanicus_blueprintskill.skill_id = mechanicus_skill.id where mechanicus_blueprintskill.blueprint_id = %s)'

def getCanMakeItemByCandidates(characters, blueprint):
    rtn = []
    for character in characters:
        if isCanMakeItem(character, blueprint):
            rtn.append(character)
    return rtn

class createJobForm(ModelForm):
    user = None
    
    class Meta:
        model = Job
        fields = ['blueprint', 'quantity']
        
    def __init__(self, user, *args, **kwargs):
        super(createJobForm, self).__init__(*args, **kwargs)
        self.empty_label=None
        self.user = user
        self.fields['blueprint'].queryset = allBpsQueryset
        self.fields['blueprint'].label_from_instance = lambda obj: allBpsLabelset[obj] if obj in allBpsLabelset else 'Invalid Item'
        
    def save(self, commit=True):
        formResult = super(createJobForm, self).save(commit=False)
        formResult.creator = self.user
        formResult.save()
        formResult.root = formResult
        formResult.parent = formResult
        formResult.save()
        formResult.createChildJobs()

class updateJobForm(ModelForm):
    user = None
    class Meta:
        model = Job
        fields = ['blueprint', 'quantity']

    def __init__(self, user, *args, **kwargs):
        super(updateJobForm, self).__init__(*args, **kwargs)
        self.empty_label=None
        self.user = user
        self.fields['blueprint'].initial = self.instance.blueprint
        self.fields['blueprint'].label_from_instance = lambda obj: allBpsLabelset[obj] if obj in allBpsLabelset else 'Invalid Item'
        self.fields['blueprint'].disabled = True
        self.fields['quantity'].initial = self.instance.quantity

    def save(self, commit=True):
        formResult = super(updateJobForm, self).save(commit=False)
        formResult.save()

class deleteJobForm(ModelForm):
    class Meta:
        model = Job
        fields = []

    confirm = BooleanField()
    
    def __init__(self, user, *args, **kwargs):
        super(deleteJobForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        formResult = super(deleteJobForm, self).save(commit=False)
        if self.cleaned_data['confirm']:
            formResult.delete()

class assignJobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['blueprint', 'quantity', 'assignee']
        user = None
    
    assignChildren = BooleanField()
        
    def __init__(self, user, *args, **kwargs):
        super(assignJobForm, self).__init__(*args, **kwargs)
        self.empty_label=None
        self.user = user
        self.fields['blueprint'].initial = self.instance.blueprint
        self.fields['blueprint'].label_from_instance = lambda obj: allBpsLabelset[obj] if obj in allBpsLabelset else 'Invalid Item'
        self.fields['blueprint'].disabled = True
        self.fields['quantity'].initial = self.instance.quantity
        assigneeQueryset = EveCharacter.objects.raw(CharSkillQuery,[self.instance.blueprint.id, self.instance.blueprint.id])
        self.fields['assignee'].queryset = EveCharacter.objects.filter(id__in=[a.id for a in assigneeQueryset])
        self.fields['assignChildren'].label = "Also assign all child jobs?"
        self.fields['assignChildren'].required = False

    def save(self, commit=True):
        formResult = super(assignJobForm, self).save(commit=False)
        formResult.assigner = self.user
        formResult.save()
        if self.cleaned_data['assignChildren']:
            formResult.assignChildJobs(formResult.assignee, formResult.assigner)

class unassignJobForm(ModelForm):
    class Meta:
        model = Job
        fields = []
        user = None

    confirm = BooleanField()
    unassignChildren = BooleanField()
    
    def __init__(self, user, *args, **kwargs):
        super(unassignJobForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['unassignChildren'].label = "Also unassign all child jobs?"
        self.fields['unassignChildren'].required = False

    def save(self, commit=True):
        formResult = super(unassignJobForm, self).save(commit=False)
        if self.cleaned_data['confirm']:
            formResult.assignee=None
            formResult.assigner=self.user
            formResult.save()
            if self.cleaned_data['unassignChildren']:
                formResult.unassignChildJobs(formResult.assigner)