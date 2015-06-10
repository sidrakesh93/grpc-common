# Performance database server

The performance database server is responsible for:

1. Collecting performance metrics data such as Queries Per Second (QPS), Percentile Latencies, Server and Client times, etc. from the clients and writing them to a database. The database has been implemented using [LevelDb](http://leveldb.org/).
