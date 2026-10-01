# The Juice Press
[Main Website](https://thejuicepress.invigoro.me)

The site is built by GitHub Pages from the files in this repository. Every push to `main` rebuilds it, which usually takes about a minute.

## Writing an article or quiz

Each article is a Markdown file in `articles/`, and each quiz is a Markdown file in `quizzes/`. Start from the template in that folder:

1. **Copy the template.** Copy `articles/_template.md` (or `quizzes/_template.md`) to a new file in the same folder. The file name becomes the page's address: `articles/local-man-wins.md` is published at `/articles/local-man-wins/`. Use lowercase words joined by hyphens, and don't start the name with `_`, because Jekyll skips those files. That's how the templates stay off the site.
2. **Write it.** Fill in the fields at the top of the file and replace the example content. The notes in each template explain the fields; the quiz template also explains how results and points work.
3. **Save drafts as often as you like.** The template starts with `published: false`, so you can commit and push your work in progress and it won't appear anywhere on the site.
4. **Publish.** When it's ready, set `date` to the publication date, change `published: false` to `published: true`, and push. The article or quiz then gets its own page, appears in the Articles or Quizzes list, and shows up on the home page if it's one of the newest.

You can do all of this on github.com without installing anything. Open the template, click **Raw** and copy everything, then go to the `articles/` or `quizzes/` folder, choose **Add file → Create new file**, paste, name the file, and commit.

### Drafts are hidden, not private

Drafts never appear on the site, but this repository is public, so anyone browsing it on GitHub can read them.

### Taking something down

Change `published: true` back to `published: false` and push. The page is removed from the site, and links people have shared to it will stop working.

### If the site stops updating

A typo in the section at the top of a file (between the two `---` lines) makes the build fail. This applies to drafts too. When that happens, the live site stays on its last good version until the typo is fixed. GitHub marks the commit as failed, and the failed "pages build and deployment" run in the **Actions** tab names the file and line. Common causes:

- a missing quotation mark
- a colon in a title that isn't in quotes
- (in quizzes) indentation that doesn't line up with the rest of the file

Comparing your file against its template usually shows the problem.

### Previewing on your own computer (optional)

If you have Ruby and Bundler installed, run this from the repository folder:

```
bundle install
bundle exec jekyll serve --unpublished
```

Then open http://localhost:4000. The `--unpublished` flag includes drafts in the preview. Leave it off to see exactly what the live site will show.
