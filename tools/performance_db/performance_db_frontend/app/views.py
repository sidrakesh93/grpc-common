from django.shortcuts import render
from user_data import UserData

def displayLeaderboard(request):
  metricstable = allUsersData()
  return render(request, 'leaderboard.html', {'metricstable': metricstable})

def plotGeneralStatistic(request, metric):
  return plotRenderer(request, metric)

def plotRenderer(request, metric):
  data = allUsersSingleMetricData(metric)
  return render(request, 'general_plots.html', {'metric': getMetricFullDesc(metric), 'data': data})

def plotUserMetrics(request, clientid):
  completeData = singleUserData(clientid)
  return render(request, 'user_plots.html', {'user_name': completeData[0].name, 'user_link':completeData[0].link, 'userdata':completeData[1]})

def getMetricFullDesc(metric):
  if metric == 'QPS':
    metricName = 'Queries Per Second'
  elif metric == 'p50':
    metricName = '50th Percentile Latency'
  elif metric == 'p90':
    metricName = '90th Percentile Latency'
  elif metric == 'p95':
    metricName = '95th Percentile Latency'
  elif metric == 'p99':
    metricName = '99th Percentile Latency'
  elif metric == 'p99point9':
    metricName = '99.9th Percentile Latency'

  return metricName

def singleUserData(clientId):
  userData = UserData('/tmp/clientmetricsdb')
  return userData.getSingleUserData(clientId)

def allUsersData():
  userData = UserData('/tmp/clientmetricsdb')
  return userData.getAllUsersData()

def allUsersSingleMetricData(metric):
  userData = UserData('/tmp/clientmetricsdb')
  return userData.getAllUsersSingleMetricData(metric)