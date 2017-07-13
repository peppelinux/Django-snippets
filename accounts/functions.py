from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


@login_required
def Form_save(request, modelform, model, url, template, templateform, 
              diz, url_suffix=None, url_kwargs=None, data_alt=None):
    """
       modelform:
       model:
       url:   url reverse string. Where to be redirected if data is valid
       template: string, a django template.html
       templateform: string, bound to that form with that values
       diz: 
       url_suffix: example #biography or ?val=key
    """
    if data_alt:
        data = data_alt
    else:
        data = dict(request.POST.items())
    
    print(data)
    
    #~ cleaned_data['utente'] = request.user
    cleaned_data = {}
    for i in data:
        if data[i] and i != 'csrfmiddlewaretoken':
            cleaned_data[i] = data[i]
    
    data_form = modelform(data=data)
    print(cleaned_data)
    
    if data_form.is_valid():            
        #~ model.objects.create(**cleaned_data)
        data_form.save()
        if url_suffix:
            dest = reverse(url, url_kwargs)+url_suffix
        else:
            dest = reverse(url, url_kwargs)
        return HttpResponseRedirect(dest)
    else:
        #    print(cleaned_data)
        #~ print(data_form.errors)
        #~ print(data)
        diz['form'] = data_form
    
    return render(request, templateform, diz)

@login_required
def Form_update(request, pk, modelform, model, template, url, 
                url_suffix=None, url_args=None, data_alt=None):
    user = request.user
    
    # qui applicare permessi
    obj = get_object_or_404(model, pk=pk, created_by=user)
    
    form = modelform(instance=obj)
    
    if data_alt:
        data = data_alt
    else:
        data = dict(request.POST.items())

    data = dict(request.POST.items())        
    #cleaned_data['user'] = user.pk
    if data.get('csrfmiddlewaretoken'): 
        del(data['csrfmiddlewaretoken'])
    form = modelform(data=data, instance=obj )
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(url, url_kwargs)+url_suffix)
    
    diz =  {
            
            }
    
    return render(request, template,diz)
