import user_data_pb2
import qpstest_pb2
import re
from collections import defaultdict

class UserData(object):

  def __init__(self, database):
    self.address = '0.0.0.0'
    self.port = 50052

  def parseTimeString(self, timeString):
    parsedTimeList = re.split('\W+', timeString)
    parsed = {}
    parsed['year'] = parsedTimeList[0]
    parsed['month'] = parsedTimeList[1]
    parsed['day'] = parsedTimeList[2]
    parsed['hour'] = parsedTimeList[3]
    parsed['min'] = parsedTimeList[4]
    parsed['sec'] = parsedTimeList[5]
    return parsed

  def getSingleUserData(self, userId):
    with user_data_pb2.early_adopter_create_UserDataTransfer_stub(self.address, self.port) as stub:
      singleUserRetrieveRequest = user_data_pb2.SingleUserRetrieveRequest()
      singleUserRetrieveRequest.user_id = userId
      
      _TIMEOUT_SECONDS = 10

      userData_future = stub.RetrieveSingleUserData.async(singleUserRetrieveRequest, _TIMEOUT_SECONDS)
      userData = userData_future.result()

      sortedClientData = sorted(userData.details.data_details, key=lambda dataDetail: dataDetail.timestamp)

      qpsList = []
      qpsPerCoreList = []
      latList = []
      timesList = []

      for dataDetail in sortedClientData:
        timestampDict = self.parseTimeString(dataDetail.timestamp)

        if dataDetail.metrics.qps != 0.0:
          qpsList.append([timestampDict,round(dataDetail.metrics.qps,1)])

        if dataDetail.metrics.qps_per_core != 0.0:
          qpsPerCoreList.append([timestampDict,round(dataDetail.metrics.qps_per_core,1)])
        
        if dataDetail.metrics.perc_lat_50 != 0.0 and dataDetail.metrics.perc_lat_90 != 0.0 and dataDetail.metrics.perc_lat_95 != 0.0 and dataDetail.metrics.perc_lat_99 != 0.0 and dataDetail.metrics.perc_lat_99_point_9 != 0.0:
          latDict = {}
          latDict['perc_lat_50'] = round(dataDetail.metrics.perc_lat_50,1)
          latDict['perc_lat_90'] = round(dataDetail.metrics.perc_lat_90,1)
          latDict['perc_lat_95'] = round(dataDetail.metrics.perc_lat_95,1)
          latDict['perc_lat_99'] = round(dataDetail.metrics.perc_lat_99,1)
          latDict['perc_lat_99_point_9'] = round(dataDetail.metrics.perc_lat_99_point_9,1)
          latList.append([timestampDict,latDict])
        
        if dataDetail.metrics.server_system_time != 0.0 and dataDetail.metrics.server_user_time != 0.0 and dataDetail.metrics.client_system_time != 0.0 and dataDetail.metrics.client_user_time != 0.0:
          timesDict = {}
          timesDict['server_system_time'] = round(dataDetail.metrics.server_system_time,1)
          timesDict['server_user_time'] = round(dataDetail.metrics.server_user_time,1)
          timesDict['client_system_time'] = round(dataDetail.metrics.client_system_time,1)
          timesDict['client_user_time'] = round(dataDetail.metrics.client_user_time,1)
          timesList.append([timestampDict,timesDict])

      dataDict = defaultdict(list)
      dataDict['qpsData'] = qpsList
      dataDict['qpsPerCoreData'] = qpsPerCoreList
      dataDict['latData'] = latList
      dataDict['timesData'] = timesList
      
      return [userData.details.user_details, dataDict]

  def validValue(self, val):
    if val != 0.0:
      return round(val,1)
    else:
      return '-'

  def getServerConfigDict(self, serverConfig):
    serverConfigDict = {}

    if serverConfig.server_type == qpstest_pb2.SYNCHRONOUS_SERVER:
      serverConfigDict['server_type'] = 'Synchronous'
    elif serverConfig.server_type == qpstest_pb2.ASYNC_SERVER:
      serverConfigDict['server_type'] = 'Asynchronous'

    serverConfigDict['threads'] = str(serverConfig.threads)
    serverConfigDict['enable_ssl'] = str(serverConfig.enable_ssl)
    serverConfigDict['host'] = str(serverConfig.host)

    return serverConfigDict

  def getClientConfigDict(self, clientConfig):
    clientConfigDict = {}

    if clientConfig.client_type == qpstest_pb2.SYNCHRONOUS_CLIENT:
      clientConfigDict['client_type'] = 'Synchronous'
    elif clientConfig.client_type == qpstest_pb2.ASYNC_CLIENT:
      clientConfigDict['client_type'] = 'Asynchronous'

    clientConfigDict['outstanding_rpcs_per_channel'] = str(clientConfig.outstanding_rpcs_per_channel)
    clientConfigDict['client_channels'] = str(clientConfig.client_channels)
    clientConfigDict['payload_size'] = str(clientConfig.payload_size)
    clientConfigDict['async_client_threads'] = str(clientConfig.async_client_threads)
    
    if clientConfig.rpc_type == qpstest_pb2.UNARY:
      clientConfigDict['rpc_type'] = 'Unary'
    elif clientConfig.rpc_type == qpstest_pb2.STREAMING:
      clientConfigDict['rpc_type'] = 'Streaming'

    clientConfigDict['enable_ssl'] = str(clientConfig.enable_ssl)
    clientConfigDict['host'] = str(clientConfig.host)

    return clientConfigDict

  def getAllUsersData(self):
    metricsTable = []
    #configsDict = {}

    _TIMEOUT_SECONDS = 10

    with user_data_pb2.early_adopter_create_UserDataTransfer_stub(self.address, self.port) as stub:
      allUsersRetrieveRequest = user_data_pb2.AllUsersRetrieveRequest()
      allUsersData_future = stub.RetrieveAllUsersData.async(allUsersRetrieveRequest, _TIMEOUT_SECONDS)
      allUsersData = allUsersData_future.result()

      for userData in allUsersData.user_data:
        for dataDetail in userData.data_details:
          userMetricsDict = {}
          userMetricsDict['id'] = str(userData.user_details.id)
          userMetricsDict['name'] = str(userData.user_details.name)
          userMetricsDict['timestamp'] = str(dataDetail.timestamp)
          userMetricsDict['test_name'] = str(dataDetail.test_name)
          userMetricsDict['qps'] = str(self.validValue(dataDetail.metrics.qps))
          userMetricsDict['qps_per_core'] = str(self.validValue(dataDetail.metrics.qps_per_core))
          userMetricsDict['perc_lat_50'] = str(self.validValue(dataDetail.metrics.perc_lat_50))
          userMetricsDict['perc_lat_90'] = str(self.validValue(dataDetail.metrics.perc_lat_90))
          userMetricsDict['perc_lat_95'] = str(self.validValue(dataDetail.metrics.perc_lat_95))
          userMetricsDict['perc_lat_99'] = str(self.validValue(dataDetail.metrics.perc_lat_99))
          userMetricsDict['perc_lat_99_point_9'] = str(self.validValue(dataDetail.metrics.perc_lat_99_point_9))
          userMetricsDict['server_system_time'] = str(self.validValue(dataDetail.metrics.server_system_time))
          userMetricsDict['server_user_time'] = str(self.validValue(dataDetail.metrics.server_user_time))
          userMetricsDict['client_system_time'] = str(self.validValue(dataDetail.metrics.client_system_time))
          userMetricsDict['client_user_time'] = str(self.validValue(dataDetail.metrics.client_user_time))
          userMetricsDict['server_config'] = self.getServerConfigDict(dataDetail.server_config)
          userMetricsDict['client_config'] = self.getClientConfigDict(dataDetail.client_config)

          metricsTable.append(userMetricsDict)

    m = sorted(metricsTable, key=lambda item: item['timestamp'], reverse=True)

    return m

  def getAllUsersSingleMetricData(self, metric):
    metricList = []

    _TIMEOUT_SECONDS = 10

    with user_data_pb2.early_adopter_create_UserDataTransfer_stub(self.address, self.port) as stub:
      allUsersRetrieveRequest = user_data_pb2.AllUsersRetrieveRequest()
      allUsersData_future = stub.RetrieveAllUsersData.async(allUsersRetrieveRequest, _TIMEOUT_SECONDS)
      allUsersData = allUsersData_future.result()

      for userData in allUsersData.user_data:
        for dataDetail in userData.data_details:
          userMetricsDict = self.parseTimeString(dataDetail.timestamp)

          if metric == 'QPS':
            userMetricsDict['value'] = round(dataDetail.metrics.qps,1)
          elif metric == 'QPSPerCore':
            userMetricsDict['value'] = round(dataDetail.metrics.qps_per_core,1)
          elif metric == 'p50':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_50,1)
          elif metric == 'p90':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_90,1)
          elif metric == 'p95':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_95,1)
          elif metric == 'p99':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_99,1)
          elif metric == 'p99point9':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_99_point_9,1)
          elif metric == 'serverSysTime':
            userMetricsDict['value'] = round(dataDetail.metrics.server_system_time,1)
          elif metric == 'serverUserTime':
            userMetricsDict['value'] = round(dataDetail.metrics.server_user_time,1)
          elif metric == 'clientSysTime':
            userMetricsDict['value'] = round(dataDetail.metrics.client_system_time,1)
          elif metric == 'clientUserTime':
            userMetricsDict['value'] = round(dataDetail.metrics.client_user_time,1)

          metricList.append(userMetricsDict)

    return metricList


