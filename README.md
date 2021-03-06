# SocialAggregator training project

[![Build Status](https://travis-ci.org/Maxbey/socialaggregator.svg?branch=master)](https://travis-ci.org/Maxbey/socialaggregator)
[![codecov.io](https://codecov.io/gh/Maxbey/socialaggregator/branch/master/graphs/badge.svg)](https://codecov.io/gh/Maxbey/socialaggregator/branch/master/)

SocialAggregator is a small project, created to improve skills of working with Django and AngularJS
## Demo
http://d1yufmp7734ayp.cloudfront.net/

(email sending is not working)

## API documentation
http://docs.socialaggregator-api.surge.sh/

## Deployment on Amazon Web Services
### AWS Access
To provide access to your aws account you must define several env variables:
 - **`AWS_ACCESS_KEY_ID`**
 - **`AWS_SECRET_ACCESS_KEY`**

### Backend
In order to deploy the backend in multicontainer Docker environment of [Elastic Beanstalk] (https://aws.amazon.com/elasticbeanstalk/details/) service, you must install and configure [ebs-deploy](https://github.com/briandilley/ebs-deploy).

#### Docker
For backend deployment used [maxbey/socialaggregator_django](https://hub.docker.com/r/maxbey/socialaggregator_django/) image, which is also located in `socialaggregator/Dockerfile` and can be manually changed by you.

Note that the **container has two scenarios**: launch gunicorn workers or run celery workers.
The behavior of the container is determined by the **`CONTAINER_BEHAVIOUR`** environment variable.

#### Sentry
Out of the box project is configured to work with [Sentry](https://sentry.io/welcome/), you just have to specify the DSN, define the env variable **`SENTRY_PRIVATE_DSN`**.

#### Environment variables
To deploy the backend application you must define a set of env variables:

##### AWS configuration
 - **`AWS_BEANSTALK_BUCKET_NAME`**

##### Django configuration
 - **`SECRET_KEY`**

For deeper understanding, please read about the [django secret](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY).

##### Storages
 - **`DATABASE_URL`**
 - **`REDIS_URL`**

Read about [URL-based configurations](https://django-configurations.readthedocs.io/en/stable/values/#url-based-values)
##### Email sending
  - **`EMAIL_HOST`**
  - **`EMAIL_HOST_USER`**
  - **`EMAIL_HOST_PASSWORD`**
 
Read about [email sending configuration](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-EMAIL_HOST) in django.

##### Social auth credentials
For deeper understanding, please read about the [python-social-auth](http://psa.matiasaguirre.net/docs/index.html) module.

[Facebook](http://psa.matiasaguirre.net/docs/backends/facebook.html)
 - **`SOCIAL_AUTH_FACEBOOK_KEY`**
 - **`SOCIAL_AUTH_FACEBOOK_SECRET`**

[GitHub](http://psa.matiasaguirre.net/docs/backends/github.html)
 - **`SOCIAL_AUTH_GITHUB_KEY`**
 - **`SOCIAL_AUTH_GITHUB_SECRET`**

[Twitter](http://psa.matiasaguirre.net/docs/backends/twitter.html)
 - **`SOCIAL_AUTH_TWITTER_KEY`**
 - **`SOCIAL_AUTH_TWITTER_SECRET`**

##### Linking with front-end
 - **`FRONTEND_URI`** (link to the front-end app)
 - **`FRONTEND_CONFIRMATION_URI`** (link to the front-end view for user`s email confirmation)
 - **`FRONTEND_RESET_PASSWORD_URI`** (link to the front-end view for user`s password resetting)

Next, you must perform: `ebs-deploy deploy -e yourenvname`

### Frontend
To deploy the frontend application it is recommended to use [S3](https://aws.amazon.com/s3/details/) and [CloudFront](https://aws.amazon.com/cloudfront/) services.

#### Sentry
Out of the box project is configured to work with [Sentry](https://sentry.io/welcome/), you just have to specify the DSN, define the env variable **`SENTRY_PUBLIC_DSN`**.

#### Environment variables
To build and deploy the front-end application you must define a set of env variables:
##### Linking with backend
 - **`BACKEND_HOST`**

##### Social auth credentials
For deeper understanding, please read about the [satellizer](https://github.com/sahat/satellizer) module.
 - **`SOCIAL_AUTH_FACEBOOK_KEY`**
 - **`SOCIAL_AUTH_GITHUB_KEY`**

##### AWS configuration
 - **`AWS_REGION`**
 - **`AWS_CLOUDFRONT_BUCKET`**
 - **`AWS_CLOUDFRONT_DISTRIBUTION`**

#### Building
To build the front-end app you must perform:
 - `npm install`
 - `npm run-script compile`

#### Deploy
For frontend deployment written special gulp task that uses [gulp-awspublish](https://www.npmjs.com/package/gulp-awspublish) and [gulp-cloudfront-invalidate-aws-publish](https://www.npmjs.com/package/gulp-cloudfront-invalidate-aws-publish) npm packages.

Next, all that remains to do is to invoke a gulp task: `gulp s3deploy`

