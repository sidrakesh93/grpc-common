# Performance database front-end

This folder contains the source code for the web front-end of the performance database service, for diplaying user test metrics such as Queries Per Seconds (QPS), Percentile Latencies, Server and Client times, etc., and has been implemented using [Django](https://www.djangoproject.com/) and [Bootstrap](http://getbootstrap.com/).

The front end can display four types of pages, including:
* **Performance database table page**: The database table for displaying the performance metrics. It has been implemented using [Bootstrap table](https://github.com/wenzhixin/bootstrap-table). It supports features for searching and sorting on the columns, as well as displaying or hiding columns as per our requirement. It displays:
  * User name: Name of the user who submits this test result
  * Timestamp: Time when the databse received the data fron the user
  * Test: Name of the test
  * Queries per seconds (QPS)
  * QPS per core
  * 50th Percentile Latency (in μs)
  * 90th Percentile Latency (in μs)
  * 95th Percentile Latency (in μs)
  * 99th Percentile Latency (in μs)
  * 99.9th Percentile Latency (in μs)
  * Server system time percentage
  * Server user time percentage
  * Client system time percentage
  * Client user time percentage

* **User statistics page**: The user statistics page can be accessed by clicking the hyperlinked name of the user in the performance database table page. The user statistics are displayed using 5 line charts, each plotting the value of particular metrics against time. The line charts are generated using the [Google charts API](https://developers.google.com/chart/interactive/docs/gallery/linechart). These line charts indicate how the different performance metrics vary for the user over time, in a specified time frame. The time frame is determined using [Date range picker](https://github.com/dangrossman/bootstrap-daterangepicker). The charts include:
  * Queries per second (QPS) chart
  * QPS per core chart
  * Percentile latencies chart
  * Server times chart: Plots the server system time and server user time.
  * Client times chart: Plots the client system time and client user time.

* **General statistics page**: The general statistics page displays the Histograms for various performance metrics, using the performance data for all the users in a given time frame. The histograms are generated using the [Google charts API](https://developers.google.com/chart/interactive/docs/gallery/histogram), while the time range is implemented using [Date range picker](https://github.com/dangrossman/bootstrap-daterangepicker). Each performance metric is displayed on a different general statistics page.
