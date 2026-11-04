# Website on openstitch.treemont-studio.com

The site itself lives in `../site` and is published by GitHub Pages. This Worker only passes
requests on to GitHub Pages, so every change to the site appears here too, without redeploying.

Deploy changes to the Worker itself (not needed for site changes):

```bash
npm install
npx wrangler login
npx wrangler deploy
```
