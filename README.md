This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

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
3. Create a production build of your app and deploy
    
    ```npm run deploy```
    * This will deploy your app and make it available using the homepage url provided in the previous step.
    * This will also create a `gh-pages` branch that contains the built app code (reflecting the deployed React app), the master branch should contain the source code for development.

