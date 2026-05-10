---
layout: page
title: Articles
permalink: /articles/
article: false
---

<ul class="post-list">
{% assign article_pages = site.pages | where_exp: "p", "p.path contains 'articles/' and p.name != 'index.md'" | sort: "date" | reverse %}
{% for p in article_pages %}
  <li>
    <span class="post-meta">{{ p.date | date: "%b %-d, %Y" }}{% assign a = p.author | default: "" | strip %}{% if a != "" %} · By {{ a }}{% endif %}</span>
    <h3>
      <a class="post-link" href="{{ p.url | relative_url }}">{{ p.title }}</a>
    </h3>
  </li>
{% endfor %}
</ul>
