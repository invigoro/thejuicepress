---
layout: page
title: ""
permalink: /
---
# The Juice Press
Welcome to **The Juice Press** --- here to bring you the daily squeeze.

## Latest articles

<ul class="post-list">
{% assign article_pages = site.pages | where_exp: "p", "p.path contains 'articles/'" | where_exp: "p", "p.name != 'index.md'" | sort: "date" | reverse %}
{% for p in article_pages limit:3 %}
  <li>
    <span class="post-meta">{{ p.date | date: "%b %-d, %Y" }}{% assign a = p.author | default: "" | strip %}{% if a != "" %} · By {{ a }}{% endif %}</span>
    <h3>
      <a class="post-link" href="{{ p.url | relative_url }}">{{ p.title }}</a>
    </h3>
  </li>
{% endfor %}
</ul>

<p><a href="{{ '/articles/' | relative_url }}">All articles</a></p>

## Latest quizzes

<ul class="post-list">
{% assign quiz_pages = site.pages | where_exp: "p", "p.path contains 'quizzes/'" | where_exp: "p", "p.name != 'index.md'" | sort: "date" | reverse %}
{% for p in quiz_pages limit:3 %}
  <li>
    <span class="post-meta">{{ p.date | date: "%b %-d, %Y" }}</span>
    <h3>
      <a class="post-link" href="{{ p.url | relative_url }}">{{ p.title }}</a>
    </h3>
  </li>
{% endfor %}
</ul>

<p><a href="{{ '/quizzes/' | relative_url }}">All quizzes</a></p>
