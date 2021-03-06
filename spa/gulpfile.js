// Generated on 2016-07-13 using generator-angular 0.15.1
'use strict';

var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var openURL = require('open');
var lazypipe = require('lazypipe');
var rimraf = require('rimraf');
var wiredep = require('wiredep').stream;
var runSequence = require('run-sequence');
var process = require('process');
var karma = require('karma');
var argv = require('yargs').argv;

var awspublish = require('gulp-awspublish');
var cloudfront = require('gulp-cloudfront-invalidate-aws-publish');
var gulpNgConstant = require('gulp-ng-constant');

var yeoman = {
  app: require('./bower.json').appPath || 'app',
  dist: 'dist'
};

var paths = {
  scripts: [yeoman.app + '/scripts/**/*.js'],
  styles: [yeoman.app + '/styles/**/*.scss'],
  test: ['test/spec/**/*.js'],
  testRequire: [


    './test/mock/**/*.js',
    './test/spec/**/*.js'
  ],
  karma: 'test/karma.conf.js',
  views: {
    main: yeoman.app + '/index.html',
    files: [yeoman.app + '/views/**/*.html']
  },
  svg: './app/images/icons/*.svg'
};

////////////////////////
// Reusable pipelines //
////////////////////////

var lintScripts = lazypipe()
  .pipe($.jshint, '.jshintrc')
  .pipe($.jshint.reporter, 'jshint-stylish');

var styles = lazypipe()
  .pipe($.sass, {
    outputStyle: 'expanded',
    precision: 10
  })
  .pipe($.autoprefixer, 'last 1 version')
  .pipe(gulp.dest, '.tmp/styles');

///////////
// Tasks //
///////////

gulp.task('config', function() {
  var config = {
    envConfig: {
      BACKEND_HOST: process.env.BACKEND_HOST,
      SENTRY_PUBLIC_DSN: process.env.SENTRY_PUBLIC_DSN,
      SOCIAL_AUTH_FACEBOOK_KEY: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
      SOCIAL_AUTH_GITHUB_KEY: process.env.SOCIAL_AUTH_GITHUB_KEY
    }
  };

  return gulpNgConstant({
      constants: config,
      stream: true
    })
    .pipe(gulp.dest('app/scripts/'));

});

gulp.task('styles', function() {
  return gulp.src(paths.styles)
    .pipe(styles());
});

gulp.task('lint:scripts', function() {
  return gulp.src(paths.scripts)
    .pipe(lintScripts());
});

gulp.task('clean:tmp', function(cb) {
  rimraf('./.tmp', cb);
});

gulp.task('start:client', ['start:server', 'styles'], function() {
  openURL('http://localhost:9000');
});

gulp.task('start:server', function() {
  $.connect.server({
    root: [yeoman.app, '.tmp'],
    livereload: true,
    // Change this to '0.0.0.0' to access the server from outside.
    port: 9000
  });
});

gulp.task('start:server:test', function() {
  $.connect.server({
    root: ['test', yeoman.app, '.tmp'],
    livereload: true,
    port: 9001
  });
});

gulp.task('watch', function() {
  $.watch(paths.styles)
    .pipe($.plumber())
    .pipe(styles())
    .pipe($.connect.reload());

  $.watch(paths.views.files)
    .pipe($.plumber())
    .pipe($.connect.reload());

  $.watch(paths.scripts)
    .pipe($.plumber())
    .pipe(lintScripts())
    .pipe($.connect.reload());

  $.watch(paths.test)
    .pipe($.plumber())
    .pipe(lintScripts());

  gulp.watch('bower.json', ['bower']);
});

gulp.task('serve', function(cb) {
  runSequence('clean:tmp', ['lint:scripts'], ['start:client'],
    'watch', cb);
});

gulp.task('serve:prod', ['build', 'config'], function() {
  $.connect.server({
    root: [yeoman.dist],
    host: '0.0.0.0',
    port: argv.port,
    fallback: yeoman.dist + '/index.html'
  });
});

gulp.task('test', function(done) {
  new karma.Server({
    configFile: __dirname + '/test/karma.conf.js',
    singleRun: true
  }, done).start();
});

// inject bower components
gulp.task('bower', function() {
  return gulp.src(paths.views.main)
    .pipe(wiredep({
      ignorePath: '..'
    }))
    .pipe(gulp.dest(yeoman.app));
});

///////////
// Build //
///////////

gulp.task('clean:dist', function(cb) {
  rimraf('./dist', cb);
});

gulp.task('client:build', ['svg', 'html', 'styles'], function() {
  var jsFilter = $.filter('**/*.js');
  var cssFilter = $.filter('**/*.css');

  return gulp.src(paths.views.main)
    .pipe($.useref({
      searchPath: [yeoman.app, '.tmp']
    }))
    .pipe(jsFilter)
    .pipe($.ngAnnotate())
    .pipe(jsFilter.restore())
    .pipe(cssFilter)
    .pipe($.minifyCss({
      cache: true
    }))
    .pipe(cssFilter.restore())
    .pipe(gulp.dest(yeoman.dist));
});

gulp.task('html', function() {
  return gulp.src(yeoman.app + '/views/**/*')
    .pipe(gulp.dest(yeoman.dist + '/views'));
});

gulp.task('images', function() {
  return gulp.src(yeoman.app + '/images/**/*')
    .pipe($.cache($.imagemin({
      optimizationLevel: 5,
      progressive: true,
      interlaced: true
    })))
    .pipe(gulp.dest(yeoman.dist + '/images'));
});

gulp.task('svg', function() {
  console.log(paths.svg);
  return gulp.src(paths.svg)
    .pipe(gulp.dest(yeoman.dist + '/svg/'));
});

gulp.task('s3deploy', function() {
  var publisher = awspublish.create({
    region: process.env.AWS_REGION,
    params: {
      Bucket: process.env.AWS_CLOUDFRONT_BUCKET
    }
  });

  var headers = {
    'Cache-Control': 'max-age=315360000, no-transform, public'
  };

  var cfSettings = {
    distribution: process.env.AWS_CLOUDFRONT_DISTRIBUTION,
    indexRootPaths: true
  };

  return gulp.src('./dist/**')
    .pipe(awspublish.gzip())
    .pipe(publisher.publish(headers))
    .pipe(cloudfront(cfSettings))
    .pipe(publisher.cache())
    .pipe(awspublish.reporter());
});

gulp.task('copy:extras', function() {
  return gulp.src(yeoman.app + '/*/.*', {
      dot: true
    })
    .pipe(gulp.dest(yeoman.dist));
});

gulp.task('copy:fonts', function() {
  return gulp.src(yeoman.app + '/fonts/**/*')
    .pipe(gulp.dest(yeoman.dist + '/fonts'));
});

gulp.task('build', ['clean:dist'], function() {
  runSequence(['images', 'copy:extras', 'copy:fonts', 'config', 'client:build']);
});

gulp.task('default', ['build']);
