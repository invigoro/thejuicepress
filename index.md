---
layout: page
title: Home
permalink: /
---

<div class="home-hero">
  <h1>The Juice Press</h1>
  <p class="home-tagline">Here to bring you the daily squeeze.</p>
</div>

## Latest articles

{% assign article_pages = site.pages | where_exp: "p", "p.path contains 'articles/'" | where_exp: "p", "p.name != 'index.md'" | sort: "date" | reverse %}
{% assign featured = article_pages | first %}

{% if featured %}
<section class="home-articles-split">
  <div class="home-articles-feature">
    <a class="home-feature-link" href="{{ featured.url | relative_url }}">
      {% assign feat_img = featured.image | default: "" | strip %}
      {% if feat_img != "" %}
      <img class="home-feature-img" src="{{ feat_img | escape }}" alt="" loading="lazy" decoding="async" />
      {% endif %}
      <div class="home-feature-body">
        <h2 class="home-feature-title">{{ featured.title | escape }}</h2>
        <p class="post-meta">{{ featured.date | date: "%b %-d, %Y" }}{% assign fa = featured.author | default: "" | strip %}{% if fa != "" %} · By {{ fa | escape }}{% endif %}</p>
        <p class="home-excerpt">{{ featured.content | strip_html | truncatewords: 50 }}</p>
      </div>
    </a>
  </div>
  <div class="home-articles-sidebar">
    {% for p in article_pages %}
      {% if forloop.index > 1 and forloop.index < 5 %}
    <a class="home-sidebar-link" href="{{ p.url | relative_url }}">
      <h3 class="home-sidebar-title">{{ p.title | escape }}</h3>
      <p class="home-excerpt">{{ p.content | strip_html | truncatewords: 25 }}</p>
    </a>
      {% endif %}
    {% endfor %}
  </div>
</section>
{% endif %}

<p class="home-all-link"><a href="{{ '/articles/' | relative_url }}">All articles</a></p>

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

<script src="{{ '/assets/js/home-post-header.js' | relative_url }}" defer></script>