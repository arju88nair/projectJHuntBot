# PCScrapy
Currently an API structure done using scrapy for culminating news from different sources and curating them Edit
Project Culminate
=========


Project Culminate,
Currently an API structure for culminating news from different sources and curating them.
Done in python

Instead of depending upon  3rd party API service for news feeds, started scrapping RSS feeds my own for independent developing and better confidence on the process


To be done in future:
1) FeedParser tag feature to not to crawl already crawled feeds
2) Have to include asynchio to increase performance
3) Have to train a model to weed out fake,corrupted,incomplete


Update:

Have created two scripts for Multithreading and Multiprocessing for the same set of URLs(nearly 60 of them)
Have to decide on which to choose to be the process for scrapping
MP uses more CPU usage with 312.5(%.2 minutes)seconds and MT uses 903.95(15 minutes)seconds
Will be running more tests by considering CPU usage and different test conditions



Licensing
=========
Project Culminate is licensed under the Apache License, Version 2.0. See
[LICENSE](https://github.com/arju88nair/PCscrapy/blob/master/LICENSE) for the full
license text.
