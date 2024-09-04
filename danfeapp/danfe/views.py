from django.shortcuts import render

def index(request):
    context = {
        'title': 'DANFE-APP',
        'description': 'O DANFE é um documento auxiliar da Nota Fiscal Eletrônica (NF-e) que tem a finalidade de documentar a operação de circulação de mercadorias ou prestação de serviços.',
        'keywords': 'danfe, nfe, nota fiscal eletrônica, documento auxiliar, circulação de mercadorias, prestação de serviços',
    }
    return render(request, 'danfe/pages/index.html', context)
