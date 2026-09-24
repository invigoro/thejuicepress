---
# QUIZ TEMPLATE
# 1. Copy this file into quizzes/ and rename it. The name becomes the URL:
#    quizzes/which-juice-are-you.md -> /quizzes/which-juice-are-you/
#    Don't start the name with "_": Jekyll skips those files, which is why this
#    template never gets a page of its own.
# 2. Fill in the fields below, then replace the intro after the closing "---".
#
# How it works:
# - Each result has a "slug" (lowercase words joined by hyphens) that names it.
#   It also makes a shareable link to that result:
#   /quizzes/which-juice-are-you/#orange-juice
# - Each answer gives "points" to one or more results, by slug. The result with
#   the most points wins; ties go to whichever result is listed first.
# - A result's "text" and the intro are Markdown. Leave a blank line between
#   paragraphs.
# - Keep the quotes around titles, prompts, and labels. Without them, answers
#   like No or Yes turn into false/true, and a colon can break the file. If the
#   text itself contains a double quote, type it as \"
# - Indentation matters, so line things up with spaces like the example does.
#   A typo up here makes the site build fail, and GitHub will show the build as
#   failed until it's fixed.
# These notes never appear on the site; delete them if you like.
title: "Which Juice Are You?"
date: 2026-09-24           # publication date (YYYY-MM-DD)
author: "Your Name"
shuffle_questions: false   # true shows the questions in a random order

results:
  - slug: orange-juice
    title: "Orange Juice"
    text: |
      Bright, dependable, and full of vitamin C. You're the reason people get out of bed in the morning.
  - slug: prune-juice
    title: "Prune Juice"
    text: |
      Nobody's first choice, but when things get stuck, you get them moving.
  - slug: pickle-juice
    title: "Pickle Juice"
    text: |
      Your friends don't understand you, but your electrolytes have never been better.

questions:
  - prompt: "When do you do your best work?"
    answers:
      - label: "First thing in the morning"
        points: { orange-juice: 10 }
      - label: "Whenever my body tells me it's time"
        points: { prune-juice: 10 }
      - label: "3 a.m., for reasons I won't get into"
        points: { pickle-juice: 10 }
  - prompt: "How would your friends describe you?"
    answers:
      - label: "A ray of sunshine"
        points: { orange-juice: 10 }
      - label: "Regular"
        points: { prune-juice: 10 }
      - label: "An acquired taste"
        points: { prune-juice: 5, pickle-juice: 5 }
---
You are what you drink. Answer a few totally scientific questions to find out which juice you really are.
