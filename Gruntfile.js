module.exports = function(grunt) {

    /*
     Loads all Grunt task plugins. You must load a task to use it here.
     Normally, you would have to write something like:
     grunt.loadNpmTask('jshint');
     grunt.loadNpmTask('karma');
     grunt.loadNpmTask('ngTemplates');
     ...for each new tasks you installed and want to use in this Gruntfile.

     But "npm install -g load-grunt-tasks" allows you to write this single line
     to load all available tasks automatically.
     */

    require('load-grunt-tasks')(grunt);

    /*
     Here goes the configuration for each task.
     General format goes like this:
     {
     : {
     : {

     }
     }
     }

     In comparison to maven:
     is like maven plugin name
     is like maven plugin's goal

     If is 'main', this is your default target which runs
     when no target parameter is given in the .registerTask() (see below)

     All file paths in this configuration are relative to the location of Gruntfile.js
     Most file paths may be specified with a glob pattern to load multiple files
     */
    grunt.initConfig({

        jshint : {
            main : {
                files : {
                    /*
                     List files you want jshint to check.
                     You want to list here your configurations, source, and test
                     js files, but do not include your library files.
                     */
                    src : [
                        '*.js',
                        'src/**/*.js',
                        'test/*.js'
                    ]
                }
            }
        },

        less : { // less task
            main : { // default target
                files : {
// take app.less, process it into a css, and save it into temp/
                    'temp/app.min.css' : ['src/styles/app.less']
                }
            }
        },

        cssmin : { // css minifier
            main : { // default target
                files : {
// take css in temp, minify it, and save it into dist
                    'dist/app.min.css' : [
                        'bower_components/bootstrap/dist/css/bootstrap.min.css',
                        'temp/app.min.css'
                    ]
                }
            }
        },

        uglify : { // minifies your js files
            main : { // default task
// again, many other options available
                options : {
                    sourceMap : true, // we will generate a source map for uglified js
                    sourceMapName : 'dist/app.min.map' // into this dir
                },
                files : {
// files to uglify and destination
// we only have one file to uglify
                    'dist/app.min.js' : ['temp/app.min.js']
                }
            }
        }
    });

    /*
     Here we can register a task to sub-tasks to run.
     Plan for building:
     1. Check for syntax and formatting errors in all files
     CSS processing:
     2. Compile .less into a .css file
     3. Minify the .css file
     JS processing:
     4. Compile all .html angular template files into a single .js file
     5. Prepare .js files for minification and concatenate all .js files into a single file
     6. Obfuscate the concatenated .js file
     */
    grunt.registerTask('build', ['jshint', 'less', 'cssmin', 'uglify']);

};