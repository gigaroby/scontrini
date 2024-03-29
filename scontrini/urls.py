"""scontrini URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib import admin


from scontrini.main.views import ReceiptNewView, UploadView, ReceiptUpdate, ReceiptShopSelect, ReceiptListView,\
    StatisticsView, ReceiptDetail

urlpatterns = [
    url(r'^$', ReceiptListView.as_view(), name='home'),

    url(r'^admin/', admin.site.urls),

    url(r'^new/$', ReceiptNewView.as_view(), name='new-receipt'),
    url(r'^upload/$', UploadView.as_view()),
    url(r'^edit/(?P<pk>\d+)$', ReceiptUpdate.as_view()),
    url(r'^select/(?P<pk>\d+)$', ReceiptShopSelect.as_view(), name='select-receipt'),
    url(r'^detail/(?P<pk>\d+)$', ReceiptDetail.as_view(), name='detail-receipt'),

    url(r'^stats/$', StatisticsView.as_view(), name='view-stats'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

