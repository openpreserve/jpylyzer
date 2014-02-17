---
layout: page
title: jpylyzer
---
{% include JB/setup %}

##About jpylyzer
*Jpylyzer* is a validator and feature extractor for *JP2* images. *JP2* is the still image format that is defined by [Part 1](http://www.jpeg.org/public/15444-1annexi.pdf) of the [JPEG 2000](http://www.jpeg.org/jpeg2000/) image compression standard (ISO/IEC 15444-1).

This tool was specifically created to answer the following questions that you might have about a *JP2* file:

1. Is this really a *JP2*, and does it conform to the format&#8217;s specifications (validation)?
2. What are the technical characteristics of the image (feature extraction)?

##Getting started
* [Installation instructions]({{ BASE_PATH }}/installation.html)

* [Using jpylyzer]({{ BASE_PATH }}/usage.html)


##License
*Jpylyzer* is free software: you can redistribute it and/or modify
it under the terms of the [GNU Lesser General Public License](https://www.gnu.org/licenses/lgpl.html) as published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

##Funding
The development of jpylyzer was partially funded by the EU FP 7 project [*SCAPE* (SCAlabable Preservation Environments)](http://www.scape-project.eu/).

##News

{% for post in paginator.posts %}
   <div class="post-entry">
   <h3><a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a> <small>{{ post.date | date_to_string }}</small></h3>
   <!-- This creates excerpt based on user-defined separator (which needs to be inserted in each post! -->
   {{ post.content | split: '<!-- more -->' | first }}
   <small><a href="{{ BASE_PATH }}{{ post.url }}">More ...</a></small>
   </div>
{% endfor %}

<!-- Pagination links -->

{% if paginator.total_pages > 1 %}
<div class="pagination">
  {% if paginator.previous_page %}
    <a href="{{ paginator.previous_page_path | prepend: site.baseurl | replace: '//', '/' }}">&laquo; Prev</a>
  {% else %}
    <span>&laquo; Prev</span>
  {% endif %}

  {% for page in (1..paginator.total_pages) %}
    {% if page == paginator.page %}
      <em>{{ page }}</em>
    {% elsif page == 1 %}
      <a href="{{ '/index.html' | prepend: site.baseurl | replace: '//', '/' }}">{{ page }}</a>
    {% else %}
      <a href="{{ site.paginate_path | prepend: site.baseurl | replace: '//', '/' | replace: ':num', page }}">{{ page }}</a>
    {% endif %}
  {% endfor %}

  {% if paginator.next_page %}
    <a href="{{ paginator.next_page_path | prepend: site.baseurl | replace: '//', '/' }}">Next &raquo;</a>
  {% else %}
    <span>Next &raquo;</span>
  {% endif %}
</div>
{% endif %}


