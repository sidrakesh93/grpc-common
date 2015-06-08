from django.conf.urls import patterns, url
from app import views

urlpatterns = patterns('',
  url(r'^$', views.displayLeaderboard, name='leaderboard'),
  url(r'leaderboard', views.displayLeaderboard, name='leaderboard'),
  url(r'plotGeneral/(?P<metric>\w+)', views.plotGeneralStatistic, name='plotGeneralStatistic'),
  url(r'plotUser/(?P<clientid>\w+)', views.plotUserMetrics, name='plotUserMetrics')
)