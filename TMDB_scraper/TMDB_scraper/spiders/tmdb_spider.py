# to run 
# scrapy crawl tmdb_spider -o movies.csv -a subdir=671-harry-potter-and-the-philosopher-s-stone

import scrapy

class TmdbSpider(scrapy.Spider):
    name = 'tmdb_spider'
    def __init__(self, subdir=None, *args, **kwargs):
        self.start_urls = [f"https://www.themoviedb.org/movie/{subdir}/"]

    def parse_actor_page(self, response):
        """
        Parses TMDB actor pages.
        Yields a dictionary containing the actor's name keyed by "actor" and the movie/TV show keyed by "movie_or_TV_name" for each movie/TV show they have acted in.
        """
        #Select actor name
        actor = response.css("h2.title a::text").get()

        #Figure out which section is the "Acting" section by examining all the headers
        acting_index = response.css("div.credits_list h3::text").getall().index("Acting")
        #Select all acting roles
        acting = response.css("div.credits_list table.card.credits")[acting_index]
        for title in acting.css("a.tooltip bdi::text"):
            yield {"actor": actor, "movie_or_TV_name": title.get()}

    def parse_full_credits(self, response):
        """
        Parses TMDB "Full Cast & Crew" pages.
        Yields a scrapy.Request for the page of each cast member, with the parse_actor_page method specified in the callback argument.
        Does not return any data.
        """
        #Select only the Cast section
        cast = response.css("ol.people.credits")[0]
        #Select actor names
        for href in cast.css("p a::attr(href)").getall():
            yield scrapy.Request(response.urljoin(href), callback = self.parse_actor_page)

    def parse(self, response):
        """
        Parses TMDB movie pages.
        Yields a scrapy.Request for the "Full Cast & Crew" page, with the parse_full_credit method specified in the callback argument.
        Does not return any data.
        """
        yield scrapy.Request(response.url+"/cast/", callback = self.parse_full_credits)