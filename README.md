This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app) and deployed using GitHub pages.

## Deployment

In order to deploy this React app to GitHub pages, do the following.

**Prerequisites:**
- `node`, `npm` and `create-react-app` are installed
- Created a git repository
- Added a a remote branch using `git remote add origin https://github.com/youruser/yourrepo.git`
- Created a React app and added it to the git-repo


**Steps:**
1. Install GitHub pages (gh-pages)

    `npm install gh-pages --save-dev`

2. Prepare package.json file for deployment
   * Add a `"homepage": "https://philjay.github.io/philjay.cc"` property to the top level of your package.json file. This property should reflect the url your page should be accessible at.
   * Add the following to the `"scripts"` property: 
    ```
      "scripts": {
         //...
         "predeploy": "npm run build",
         "deploy": "gh-pages -d build"
      }
    ```
    * This will ensure that your app is built before being deployed and perform deployment using gh-pages.
    
3. Create a production build of your app and deploy
    
    ```npm run deploy```
    * This will deploy your app and make it available using the homepage url provided in the previous step.
    * This will also create a `gh-pages` branch that contains the built app code (reflecting the deployed React app), the master branch should contain the source code for development.
    
4. Be patient. It may take a couple of minutes after the `npm run deploy` command has finished before your page becomes available publicly. You can check the GitHub pages section in your repository settings to monitor the current status.


## Custom domain

In case you want your page to be available on a fully customized domain (not something starting with `"https://philjay.github.io/...` or similar), do the following.

1. Purchase the domain you would like to use, in this case `philjay.cc` (apex domain).
2. In your DNS provider custom DNS settings, add a new A record [reflecting the IP addresses of GitHub pages](https://help.github.com/en/github/working-with-github-pages/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain).
    * In my case, I created 4 A records (using @ as host), each pointing to one of the 4 GitHup pages IP addresses
    * Also make sure to remove any existing A records pointing to other IP addresses (e.g. where your site was previously hosted)
3. Wait until DNS propagation has completed, this can take up to 24 hours.
4. I would recommend to enable "Enforce HTTPS" in your repository settings for GitHub pages.
5. Create a file named `CNAME` in your project (not src) directory. This will prevent the custom-domain field in your repo settings from being overwritten by gh-pages. File content is just the domain name (change to your domain name):
   
   ```philjay.cc```
   
6. Update your `package.json` file homepage field to reflect the new domain:

    ```"homepage": "https://philjay.cc"```

7. Copy the `CNAME` file to the public folder during predeploy:

    ```
      "scripts": {
         //...
         "predeploy": "npm run build && cp CNAME public",
      }
    ```

8. Deploy your app using `npm run deploy`


## Problems with react-router

GitHub Pages doesn't natively support single page apps. When there is a **fresh page load** for a url like example.com/foo, where /foo is a frontend route, the GitHub Pages server returns 404 because it knows nothing of /foo.

 - Solution 1: [Use HashRouter](https://stackoverflow.com/a/46060999/1590502)
 - Solution 2: [Tweak your index.html](https://github.com/rafrex/spa-github-pages) (used in this project)
