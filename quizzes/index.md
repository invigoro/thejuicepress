---
layout: page
title: Quizzes
permalink: /quizzes/
quiz: false
---

<ul class="post-list">
{% assign quiz_pages = site.pages | where_exp: "p", "p.path contains 'quizzes/' and p.name != 'index.md'" | sort: "date" | reverse %}
{% for p in quiz_pages %}
  <li>
    <span class="post-meta">{{ p.date | date: "%b %-d, %Y" }}</span>
    <h3>
      <a class="post-link" href="{{ p.url | relative_url }}">{{ p.title }}</a>
    </h3>
  </li>
{% endfor %}
</ul>
