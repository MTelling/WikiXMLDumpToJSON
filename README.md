# XML Wikipedia dump to multiple JSON files
Tool to help with the DTU Course Computational Tools For Big Data but can be freely used. 
This tool consists of two parts. A Wikipedia Reader and a Wikipedia splitter. If you are just interested in converting the dump to JSON, just use the Wikipedia splitter.

This has only been tested on the dump `enwiki-20170820-pages-articles-multistream.xml`. 

## Wikipedia Reader
When downloading Wikipedia you receive about 60GB of XML data. It is impossible to keep this all in memory on most machines therefore you need to stream it. Streaming makes accessing the data a bit harder as you can't just iterate over the tree for each page. Therefore we have created a reader for the XML file, which will parse each page into a Python dictionary. This has been built with Python iterators. This means that you easily iterate over pages with the following code:
```python
wiki_reader = WikiReader(input_file)
for page_dict in wiki_reader:
	# Do something with the page
```

## Wikipedia Splitter
Having the entire Wikipedia in a single 60GB file is not very easy to work with. We'd much rather have the file split into several smaller files.

To do this we have created a Wikipedia Splitter. This uses the Wikipedia Reader to read the XML data page by page into dictionaries. After this it takes a number of pages at a time and writes them to JSON files. At the same time it writes a JSON index file, which maps each page title to a JSON file. This way we can pick out individual pages for testing. 

The Splitter consists of three commands: `split-wiki`, `get-page`, `get-pages`.
- The `split-wiki` command splits a Wikipedia XML file into several JSON files. 
- The `get-page` command gets the JSON version of a single page. You must run the split wiki command first.
- The `get-pages` command collects several pages defined in a txt file, into a single JSON file. This is useful for testing. 

To use any of the commands run `python src/WikiSplitter.py {command}`.
