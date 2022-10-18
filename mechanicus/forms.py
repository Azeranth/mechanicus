from django.forms import ModelForm,IntegerField
from django.contrib.auth.models import User

from .models import Job,Blueprint,Item,Skill,CharacterSkillMap,BlueprintOutput,BlueprintInput,BlueprintSkill

class createJobForm(ModelForm):
    quantity = IntegerField()
    class Meta:
        model = Job
        fields = ['product']
        
    
    def __init__(self, user, *args, **kwargs):
        super(createJobForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['product'].queryset = Blueprint.objects.filter(id__in=[bpoutput.blueprint_id for bpoutput in BlueprintOutput.objects.all()])
        self.fields['product'].label_from_instance = lambda obj: f"{Item.objects.get(id=BlueprintOutput.objects.get(blueprint_id=obj.id).item_id).name}"
        
    def save(self, commit=True):
        print('saving')
        instance = super(createJobForm, self).save(commit=False)
        instance.root = instance
        instance.parent = instance
        instance.creator = self.user
        instance.save()