# Bazardelux

Bazardelux.com was a search engine for finer things being sold by private
persons accross Sweden and Europe.

## Architecture

Bazardelux was made of 3 components:

* [A website](https://github.com/erwan-lemonnier/bdl-com) featuring flexible
  text search and infinite scroll, displaying a selection of finer things being
  sold by individuals across Europe through platforms such as Tradera, Blocker,
  eBay or facebook marketplace.

* [A collection of scrappers](https://github.com/erwan-lemonnier/bdl-scraper)
  running as docker containers in an autoscalling cluster, and called at
  regular intervals to scrape new interesting sale announces from multiple
  websites, or fetch the latest status on specific announces.

* [The bazardelux api](https://github.com/erwan-lemonnier/bdl-api), providing
  the APIs used by both the website and scrappers, including a lambda functions
  triggered by a scheduler and task queues.

All 3 components are implemented as [pymacaron
microservices](http://pymacaron.com): python/Flask apps tightly integrated to a
swagger specification, deployed as docker containers on amazon Beanstalk.

For an architectural overview of how the BDL API and SCRAPER interact, see
[here](https://github.com/erwan-lemonnier/bdl-api/blob/master/architecture-1.png).


## History

Bazardelux started as kluemarket.com, a market place developed by the Swedish
startup Klue in 2016. As Klue's business model evolved towards online
communities to become Lyxloppis, I purchased the right to kluemarket.com,
rebranded it into bazardelux.com and refactored it to make it highly scalable,
with a vision of making it into an aggregator covering all European peer to
peer marketplaces (ebay, leboncoin, blocket...).

I ran it for a couple of years. However, due to lack of time to focus on that
particular project, I decided to shut it down in 2020.

Before shutdown, bazardelux draw 50.000 individual visitors per months.

## Disclaimer

I am releasing this code to the public as a showcase of what can be done with
[pymacaron](http://pymacaron.com).

This code comes with no guarrantees of any kind, nor do I or Lookfar AB (owner
of this code) endorse any responsibility for this code or any usage made of it.


## Testing API and SCRAPER locally

The API and SCRAPER microservices send requests to each other. Both services
must therefore be running to get a standalone test environment. By default,
each calls the live host:port for the other, as specified in the swagger files.

Those host:port can be overriden by setting the environment variables
BDL_API_HOST and BDL_SCRAPER_HOST.

To run both services beside each other on your dev laptop, start 2 terminals and
do in each:

```shell
# Shell running the BDL API
cd bdl-api
export BDL_SCRAPER_HOST=127.0.0.1:8888
python server.py --port 8080
```

```shell
# Shell running the BDL SCRAPER
cd bdl-scraper
export BDL_API_HOST=127.0.0.1:8080
python server.py --port 8888
```
