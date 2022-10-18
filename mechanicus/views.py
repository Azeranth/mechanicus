from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.template.loader import render_to_string
from django.shortcuts import render
from allianceauth.eveonline.models import EveCharacter
from django.contrib.auth.models import User
import django.http
from esi.clients import EsiClientProvider
from esi.models import Token
from esi.decorators import token_required

from .models import Job,Blueprint,Item,Skill,CharacterSkillMap,BlueprintOutput,BlueprintInput,BlueprintSkill
esi = EsiClientProvider()

from .models import Job
from .forms import createJobForm

@login_required
@permission_required("mechanicus.basic_access")
def index(request):
    context = {"text": "Hello, World!"}
    return render(request, "mechanicus/index.html", context)
    
@login_required
@permission_required("mechanicus.job_view_open")
def jobs(request):
    user = request.user
    formActions = []
    if user.has_perm("mechanicus.jobCreate"):
        formActions.append("create")
    if user.has_perm("mechanicus.jobUpdate"):
        formActions.append("update")
    if user.has_perm("mechanicus.jobDelete"):
        formActions.append("delete")
    if user.has_perm("mechanicus.jobAssign"):
        formActions.append("assign")
    if user.has_perm("mechanicus.jobUnassign"):
        formActions.append("unassign")
    if user.has_perm("mechanicus.jobReassign"):
        formActions.append("reassign")
   
    context = { "text" : "This is the list of jobs you can see",
                "formActions" : formActions}
    
    if user.has_perm('mechanicus.job_view_all_access'):
        context.update({"job_display_list":Job.objects.all()})
    else:
        context.update({"job_display_list":Job.objects.all().filter(assignee=None)})
    return render(request, "mechanicus/jobs.html", context)

@login_required
@permission_required("mechanicus.job_view_open")
@xframe_options_exempt
def jobForm(request, action):
    action = action.lower()
    user = request.user
    instance = int(request.GET.get('instance','0'))
    isInstanceValid = Job.objects.filter(id=instance).count()
    returnAddr = request.GET.get('redirect','/mechanicus/')
    context = { "model" : "Job",
                "action" : action}
    print(request.method)
    if request.method == "POST":
        if action == "create":
            if not user.has_perm("mechanicus.jobCreate"):
                return django.http.HttpResponseForbidden("You lack the permissions to access this action")
            form = createJobForm(user,request.POST)
            print(form)
            form.save()
        elif not isInstanceValid:
                return django.http.HttpResponse("You are attempting to access an invalid instance", status=422)
        elif action == "update":
            if not user.has_perm("mechanicus.jobUpdate"):
                return django.http.HttpResponseForbidden("You lack the permissions to access this action")
            form = createJobForm(user,request.POST)
            form.save()
        elif action == "delete":
            if not user.has_perm("mechanicus.jobDelete"):
                return django.http.HttpResponseForbidden("You lack the permissions to access this action")
            form = createJobForm(user,request.POST)
            form.save()
        elif action == "assign":
            if not user.has_perm("mechanicus.jobAssign"):
                return django.http.HttpResponseForbidden("You lack the permissions to access this action")
            form = createJobForm(user,request.POST)
            form.save()
        elif action == "unassign":
            if not user.has_perm("mechanicus.jobUnassign"):
                return django.http.HttpResponseForbidden("You lack the permissions to access this action")
            form = createJobForm(user,request.POST)
            form.save()
        elif action == "reassign":
            if not user.has_perm("mechanicus.jobReassign"):
                return django.http.HttpResponseForbidden("You lack the permissions to access this action")
            form = createJobForm(user,request.POST)
            form.save()
        else:
            return django.http.HttpResponseBadRequest("The action you requested is not supported")
        return django.http.HttpResponseRedirect(returnAddr)        
    if action == "create":
        if not user.has_perm("mechanicus.jobCreate"):
            return django.http.HttpResponseForbidden("You lack the permissions to access this action")
        context.update({'form':createJobForm(user)})
    elif not isInstanceValid:
            return django.http.HttpResponse("You are attempting to access an invalid instance", status=422)
    elif action == "update":
        if not user.has_perm("mechanicus.jobUpdate"):
            return django.http.HttpResponseForbidden("You lack the permissions to access this action")
        context.update({'form':updateJobForm(user)})
    elif action == "delete":
        if not user.has_perm("mechanicus.jobDelete"):
            return django.http.HttpResponseForbidden("You lack the permissions to access this action")
        context.update({'form':deleteJobForm(user)})
    elif action == "assign":
        if not user.has_perm("mechanicus.jobAssign"):
            return django.http.HttpResponseForbidden("You lack the permissions to access this action")
        context.update({'form':assignJobForm(user)})
    elif action == "unassign":
        if not user.has_perm("mechanicus.jobUnassign"):
            return django.http.HttpResponseForbidden("You lack the permissions to access this action")
        context.update({'form':unassignJobForm(user)})
    elif action == "reassign":
        if not user.has_perm("mechanicus.jobReassign"):
            return django.http.HttpResponseForbidden("You lack the permissions to access this action")
        context.update({'form':reassignJobForm(user)})
    else:
        return django.http.HttpResponseBadRequest("The action you requested is not supported")
    return render( request, 'mechanicus/baseForm.html', context)

@login_required
@permission_required("mechanicus.basic_access")
@token_required(scopes=['esi-skills.read_skills.v1'])
def skillRegister(request, token):
    user = request.user
    skills = esi.client.Skills.get_characters_character_id_skills(character_id = token.character_id, token = token.valid_access_token()).results()['skills']

    for skill in skills:
        skillId = skill['skill_id']
        level = skill['active_skill_level']
        for i in range(level):
            if not CharacterSkillMap.objects.filter(skill=Skill.objects.get(skillId=skillId, level=i+1), character=EveCharacter.objects.get(character_id=token.character_id)).count():
                csm = CharacterSkillMap(skill=Skill.objects.get(skillId=skillId, level=i+1), character=EveCharacter.objects.get(character_id=token.character_id))
                csm.save()

    skillmapquery = list(CharacterSkillMap.objects.filter(character=EveCharacter.objects.get(character_id=token.character_id)))
    skillStringList = []
    for smq in skillmapquery:
        skillStringList.append(smq.character.character_name + ": " + smq.skill.name + " " + str(smq.skill.level))

    context = {"skillStringList": skillStringList}
    return render(request, "mechanicus/skillRegister.html", context)