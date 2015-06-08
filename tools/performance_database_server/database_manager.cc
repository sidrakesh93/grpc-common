/*
 *
 * Copyright 2015, Google Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google Inc. nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include "database_manager.h"
#include <ctime>
#include <cassert>
#include <fstream>

#define MAX_NUM_OF_SECONDS (5*365*24*60*60) // number of seconds in 5 years

namespace grpc{
namespace testing{

DatabaseManager::DatabaseManager(std::string database) {
  database_ = database;
  leveldb::Options options;

  options.create_if_missing = true;
  leveldb::Status status = leveldb::DB::Open(options, database_, &db);
  assert(status.ok());
}

DatabaseManager::~DatabaseManager() {
  delete db;
}

// Get current date/time, format is YYYY-MM-DD.HH:mm:ss
const std::string currentDateTime() {
  time_t     now = time(0);
  struct tm  tstruct;
  char       buf[80];
  tstruct = *localtime(&now);

  strftime(buf, sizeof(buf), "%Y/%m/%d, %X", &tstruct);
  return buf;
}

static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
  ((std::string*)userp)->append((char*)contents, size * nmemb);
  return size * nmemb;
}

UserDetails getUserData(std::string accessToken) {
  std::string url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + accessToken;
  CURL *curl;
  CURLcode res;
  std::string readBuffer;

  UserDetails userDetails;

  curl = curl_easy_init();
  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
    res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);

    std::string err;
    int ret = pbjson::json2pb(readBuffer, &userDetails, err);
  }

  return userDetails;
}

void DatabaseManager::recordSingleUserData(const SingleUserRecordRequest* request) {
  UserDetails userDetails = getUserData(request->access_token());

  std::string prevValue;
  leveldb::Status status = db->Get(leveldb::ReadOptions(), userDetails.id(), &prevValue);

  SingleUserDetails singleUserDetails;
  
  if(status.ok())
    singleUserDetails.ParseFromString(prevValue);
  
  DataDetails* dataDetails = singleUserDetails.add_data_details();

  dataDetails->set_timestamp(currentDateTime());
  dataDetails->set_test_name(request->test_name());
  
  *(dataDetails->mutable_metrics()) = request->metrics();
  *(dataDetails->mutable_client_config()) = request->client_config();
  *(dataDetails->mutable_server_config()) = request->server_config();
  *(singleUserDetails.mutable_user_details()) = userDetails;

  std::string newValue;
  singleUserDetails.SerializeToString(&newValue);

  status = db->Put(leveldb::WriteOptions(), userDetails.id(), newValue);
  assert(status.ok());
}

SingleUserRetrieveReply DatabaseManager::retrieveSingleUserData(const SingleUserRetrieveRequest* request) {
  std::string value;
  leveldb::Status status  = db->Get(leveldb::ReadOptions(), request->user_id(), &value); 

  SingleUserRetrieveReply singleUserRetrieveReply;
  SingleUserDetails* details = singleUserRetrieveReply.mutable_details();

  if(status.ok())
    details->ParseFromString(value);

  return singleUserRetrieveReply;
}

AllUsersRetrieveReply DatabaseManager::retrieveAllUsersData(const AllUsersRetrieveRequest* request) {
  leveldb::ReadOptions options;
  options.snapshot = db->GetSnapshot();

  leveldb::Iterator* it = db->NewIterator(options);

  AllUsersRetrieveReply allUsersRetrieveReply;

  for (it->SeekToFirst(); it->Valid(); it->Next()) {
    SingleUserDetails* singleUserDetails = allUsersRetrieveReply.add_user_data();
    singleUserDetails->ParseFromString(it->value().ToString());
  }

  assert(it->status().ok());  // Check for any errors found during the scan
  delete it;

  db->ReleaseSnapshot(options.snapshot);

  return allUsersRetrieveReply;
}

}
}