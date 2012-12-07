#!/usr/bin/env python
import os, os.path, shutil, fileinput, string, sys, re, getopt
from optparse import OptionParser
from time import gmtime, strftime

def minimizeJSfromFolder(folder):
    print "\n\nMinimizing files for "+folder+"...\n\n";
    os.system('find '+folder+" -name '*.js' -print0 | xargs -0 -I 'jspath' sh -c 'echo minimizing file: \'jspath\'; java -jar\
 yuicompressor-2.4.7.jar \'jspath\' -o \'jspath\' '");
    print "\n\nMinimizing for "+folder+"done.\n\n";

def createTarFromREPO(repo,version, gitpath):
    print "\n\nArchiving "+repo+" folder...\n\n";
    os.system('git archive --remote='+gitpath+repo+'.git ' + '-o '+repo+'.tar '+version+' -v'); 

    if (os.path.getsize(repo+'.tar')==0):
        print 'invalid repo/tag, exiting...'
        exit()
        return 0;
    else:
        print 'file created correctly'
        return 1;

def uncompressTar(repo):
    if not os.path.isdir(repo):
        os.makedirs(repo)
    print 'tar -C '+ repo + ' -xvf ' + repo+'.tar'    
    os.system('tar -C '+ repo + ' -xvf ' + repo+'.tar')

def rsyncFolder(folderSrc,folderDst,ipserver,pemfile):
    os.system('rsync -cavr  ./'+folderSrc+'/* -e "ssh -i '+pemfile+'" '+ipserver+':'+folderDst);

def createLogFile(repo,version):
    os.walk(repo)
    file = open((repo+'/deploy.txt'), 'w+')
    file.write('Date:'+strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    file.write('\nRepo:'+repo)
    file.write('\nVersion:'+version+'\n')
    file.close()

### BEGINING OF THE PROGRAM
def main():

    ### SPECIFICATION OF OPTIONS
    parser = OptionParser(usage="usage: %prog [options] repoName tag/branch",
                          version="%prog 1.0")

    parser.add_option("-s", "--ipserver",
                      action="store",
                      dest="ipserver",
                      default=False,
                      help="specify the remote server where to make the deploy, user@ip")
    
    parser.add_option("-p", "--pemfile",
                      action="store",
                      dest="pemfile",
                      default=False,
                      help="specify the pem file path in your computer to connect to the Amazon ec2 server")

    parser.add_option("-e", "--enviroment",
                      action="store",
                      dest="enviroment",
                      default=False,
                      help="specify the enviroment where to deploy the code, this value will be concatenated to te beginning of var/www/html")

    parser.add_option("-b", "--basedir",
                      action="store",
                      dest="basedir",
                      default='/var/www/html/',
                      help="specify the base url where deploying")

    parser.add_option("-g", "--basegitpath",
                      action="store",
                      dest="gitpath",
                      default='git@bitbucket.org:accedo/',
                      help="specify the base dir where git is going to connect")

    parser.add_option("-a", "--appdir",
                      action="store",
                      dest="appdir",
                      default='',
                      help="specify the app directory where deploying the app")
    
    
    (options, args) = parser.parse_args()

    ### CHECK WRONG NUMBER OF OPTIONS
    if len(args) != 2:
        parser.error("wrong number of arguments, check more info with "+sys.argv[0]+" -h")

    if (not options.ipserver):
        parser.error("you must specify an IP server like ec2-user@123.123.123.123")

    if (not options.pemfile):
        parser.error("you must specify a pem file")
        
    if not os.path.exists(options.pemfile):    
        parser.error("the pem file path you specified doesn't exists (must be an absolute path)")

    repoName = args[0]
    tagVersion = args[1];
            
    if not options.enviroment:
        enviroment=''

    else:
        enviroment=options.enviroment+'/'

    ### GENERATE THE FINAL PATH WHERE RSYNC WILL CONNECT
    finalPath=options.basedir+enviroment+options.appdir;
    os.system('clear');
    raw_input("You're going to upload to \nserver "+options.ipserver+'\nthe repo '+repoName+' \nwith tag/branch '\
                  +tagVersion+'\nto folder '+finalPath+' \n\n\npress ENTER to continue or Ctrl-C for exit\n\n\n')
    
    createTarFromREPO(repoName,tagVersion,options.gitpath);
    uncompressTar(repoName);
    createLogFile(repoName,tagVersion)
    minimizeJSfromFolder(repoName);
    rsyncFolder(repoName,finalPath,options.ipserver,options.pemfile);

if __name__ == "__main__":
        main()

