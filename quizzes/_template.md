---
# QUIZ TEMPLATE
# A quiz is two files with the same name: this page, and a data file in
# _data/quizzes/ that holds the intro, questions, and results.
# 1. Copy this file into quizzes/ and rename it. The name becomes the URL:
#    quizzes/which-juice-are-you.md -> /quizzes/which-juice-are-you/
#    Don't start the name with "_": Jekyll skips those files, which is why this
#    template never gets a page of its own.
# 2. Copy _data/quizzes/_template.json to _data/quizzes/ under the same name
#    (e.g. which-juice-are-you.json) and fill it in; see the notes below.
# 3. Fill in the fields below. Keep the quotes around the title; if the title
#    itself contains a double quote, type it as \"
# These notes never appear on the site; delete them if you like.
title: "Which Juice Are You?"
quiz_data_key: which-juice-are-you   # the data file's name, without ".json"
date: 2026-09-24                     # publication date (YYYY-MM-DD)
author: "Your Name"
#
# Filling in the data file:
# - introHtml is shown above the questions, and each result's contentHtml is
#   shown when that result wins. Both are HTML, so wrap paragraphs in <p></p>.
# - randomQuestionOrder: true shuffles the questions for each visitor.
# - Every question and answer needs a unique "id". An answer's "weights" are the
#   points it gives each result, listed by result id; results it leaves out get 0.
# - Result ids must be whole numbers. The result with the most points wins
#   (ties go to the lowest id). Its "slug" makes a shareable link to that
#   result, e.g. /quizzes/which-juice-are-you/#orange-juice
# - It's JSON, so mind the commas: every item in a list except the last needs
#   one after it.
---
