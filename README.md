# Django application for Long-read Brain dataset. 

The application can be accessed by typing [isoforms.com](isoforms.com) into the browser. 

## Deployment
The app has been deployed using AWS Elastic Beanstalk.
To redeploy the app, do the following:
- If you don't have a local copy of the repository, clone it with `git clone`.
- Make sure you're on the main branch (or whichever branch you want to deploy) and have the latest changes.
    ```bash
    git switch main
    git pull
    ```
- Archive the head of the branch into a zip file. Run the following in the top level folder of the repository (the folder containing manage.py).
    ```bash
    git archive -o ../isoVisDev.zip --format=zip HEAD
    ```
    This creates an archive of just the last commit on the current branch. Two folders (`files/` and `expression/static/`) are excluded from the archive, as defined in the file `.gitattributes`. (The gene data .txt files in the `expression/static/` folder are stored separately from the app in an AWS S3 bucket, in order to speed up deployment and reduce AWS costs. The `files/` folder isn't needed for deployment.)
- In the AWS console, go to 'Elastic Beanstalk'. You should see a list of at least one application. If it's the first time you've accessed Elastic Beanstalk, you might have to click 'Create Application' before you see any existing applications.
- Click on the application 'Isoforms-RSE', and then on its environment 'Isoforms-RSE-env'.
- Click on the 'Upload and Deploy' button (top right).
- Select the .zip file you just created and click 'Deploy'. This will normally take a few minutes. You can see progress in the 'Events' tab.

#### Uploading gene data files
The gene data .txt files are stored in the reposoitory in `expression/static/` folder, but for deployment they are stored in an AWS S3 bucket. The app is configured to read the files from the S3 bucket. You don't need to upload them again when deploying the app.

If you need to update the gene data files, you can upload them to the S3 bucket directly. The bucket is named `gene-data-bucket`, and you can access it through the AWS console by searching for 'S3' and then clicking on the bucket name. Although you can upload files using the AWS console, if you're uploading all of them it tends to take so long that you get logged out before the upload has finished. Instead, you can use the AWS CLI to upload the files. First, install the AWS CLI and configure it with your AWS credentials.
Then, run the following command to upload all `.txt` files from the `expression/static/` folder to the S3 bucket:
```bash
aws s3 sync ./expression/static/ s3://gene-data-bucket/ --profile my-sso-profile --exclude "*" --include "*.txt"
```
where `my-sso-profile` is the name of your AWS CLI profile. If you don't have a profile set up, you can use the `aws configure` command to set one up.

### AWS troubleshooting
AWS is enormously pwerful and flexible, but it can be completely overwhelming to use, and extrordinarily difficult to learn what needs doing and how to do it. Fornunately, large language models like ChatGPT are very good at providing instructions and troubleshooting problems! A good strategy with any deployment problems is to go to the 'Logs' tab in the Elastic Beanstalk environment, download the logs and then copy and paste any warnings or errors into ChatGPT. 

## Further information
More information on the initial build and deployment of this Django app can be found [here](https://szikayleung.github.io/weBook/WebResource.html).
