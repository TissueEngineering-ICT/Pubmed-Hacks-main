from django.shortcuts import render, redirect
from . import pubmed_api
from paper_abstract_app.models import Articlemodel,Journal
from django.http import HttpResponse
import csv,urllib
from .models import Journal
import pandas as pd
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def home(request):
    print("home entered")
    return render(request, 'paper_abstract_app/index.html')

@login_required
def abst(request):
    
    if request.POST['keyward']:
        keyward = request.POST['keyward']
    if 'all' in request.POST:
        num = None
    elif request.POST['num']:
        num = request.POST['num']
    if request.POST['min_date']:
        min_date = request.POST['min_date']
    if request.POST['max_date']:
        max_date = request.POST['max_date']

    Articlemodel.objects.all().delete()
    TERM         = keyward
    NUM          = num
    MIN_DATE     = min_date # yyyy/mm/dd
    MAX_DATE     = max_date # yyyy/mm/dd
   
    AbstractModel_list = pubmed_api.getArticle(TERM,MIN_DATE,MAX_DATE,NUM)
    Articlemodel.objects.bulk_create(AbstractModel_list)
    AbstractModel = {'Articles':Articlemodel.objects.all()} 
    return render(request, 'paper_abstract_app/abst.html',AbstractModel)

@login_required
def some_view(request):
    articles = Articlemodel.objects.order_by('-journal__impact_factor')
    AbstractModel = {'Articles':articles} 
    return render(request, 'paper_abstract_app/abst.html',AbstractModel)

@login_required
def csv_export(request):

    response = HttpResponse(content_type='text/csv; charset=shift_jis')

    f = "PubMed論文" + "_"  + ".csv"
    filename = urllib.parse.quote((f).encode("shift_jis"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)

    writer = csv.writer(response)
    Paper_info_list = Articlemodel.objects.all()
    header = ['PMID','Date_publish','Title','Author','Abstract','JournalTitle','SJR','DOI']
    writer.writerow(header)

    for Paper in Paper_info_list:
        try:
            row = [Paper.PMID, Paper.Date_publish, Paper.Title, Paper.Author, Paper.Abstract, Paper.journal.name, Paper.journal.impact_factor, Paper.DOI]
            writer.writerow([str(item).encode("shift_jis", errors='ignore').decode("shift_jis") for item in row])
        except:
            pass
    return response

def import_impact_factors(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']  # フォームからCSVファイルを取得する
        df = pd.read_csv(csv_file)

        for index, row in df.iterrows():
            journal_name = row['Title']  # 列の名前に応じて調整する
            impact_factor_str = str(row['SJR'])  # 列の名前に応じて調整する
            impact_factor_str = impact_factor_str.replace(',', '')  # カンマを削除する

            impact_factor = 0.0  # Set default value
            if impact_factor_str:  # Check if the string is not empty
                try:
                    impact_factor = float(impact_factor_str)
                except ValueError:
                    pass  # Leave the default value if conversion fails

            journal, created = Journal.objects.get_or_create(
                name=journal_name,
                defaults={'impact_factor': impact_factor},
            )
            if not created:
                journal.impact_factor = impact_factor
                journal.save()

        return render(request, 'import_success.html')
    else:
        return render(request, 'import_form.html')

