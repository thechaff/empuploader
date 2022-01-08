#! /usr/bin/env python3
import argparse
import configparser
import os
from pathlib import Path
config = configparser.ConfigParser(allow_no_value=True)
import subprocess
import empupload.network as network
import sys
if sys.platform=="win32":
    from consolemenu import SelectionMenu
if sys.platform!="win32":
    from simple_term_menu import TerminalMenu
import empupload.emp as emp
from shutil import which
from prompt_toolkit import prompt as input
"""
Inputs User settings into args

:param args: arguments for console or config
:return: args:
"""
def create_config(args):
    if args.config==None or os.path.exists(args.config)==False:
        print("Could not read config")
        return
    try:
        configpath=args.config
        config.read(configpath)
    except:
        print("Error accessing data from  config")
        return args
    if args.screens==None and config['general']['screens']!=None and len(config['general']['screens'])!=0:
        args.screens=config['general']['screens']
    if args.template==None and config['general']['template']!=None and len(config['general']['template'])!=0:
        args.template=config['general']['template']
    if args.font==None and config['general']['font']!=None and len(config['general']['font'])!=0:
        args.font=config['general']['fonts']
    if args.media==None and config['dirs']['media']!=None and len(config['dirs']['media'])!=0:
        args.media=config['dirs']['media']
    if args.trackerurl==None and config['general']['trackerurl']!=None and len(config['general']['trackerurl'])!=0:
        args.trackerurl=config['general']['trackerurl']
    if args.cookie==None and config['general']['cookie']!=None and len(config['general']['cookie'])!=0:
        args.cookie=config['general']['cookie']
    if args.torrents==None and config['dirs']['torrents']!=None and len(config['dirs']['torrents'])!=0:
        args.torrents=config['dirs']['torrents']
    if args.data==None and config['dirs']['data']!=None and len(config['dirs']['data'])!=0:
        args.data=config['dirs']['data']
    if args.images==None and config['dirs']['images']!=None and len(config['dirs']['images'])!=0:
        args.images=config['dirs']['data']



"""
sets up Argument Parser with required settings
:param: None
:return: parser.args:
"""
def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m','--media')
    parser.add_argument('-t','--torrents')
    parser.add_argument('-s','--screens')
    parser.add_argument('-cv','--cover')
    parser.add_argument('-g','--images')
    parser.add_argument('-tm','--template')
    parser.add_argument('-u','--trackerurl')
    parser.add_argument('-i','--input')
    parser.add_argument('-c','--config')
    parser.add_argument('-d','--data')
    parser.add_argument('-f','--font')
    parser.add_argument('-k','--cookie')
    parser.add_argument('-b','--batch',default=True)
    comd = parser.add_mutually_exclusive_group()
    comd.add_argument('-prepare', action='store_true')
    comd.add_argument('-upload', action='store_true')
    comd.add_argument('-update', action='store_true')
    comd.add_argument('-createtor', action='store_true')
    return parser.parse_args()


"""
Check if Process is Valid
    - proper arg settings for mode
    - at least one file in directory
:param args: user Commandline/Config arguments
:return: bool returns true if all paremeters are meet
"""
def check_valid(args):  
    if args.prepare==False and args.upload==False and args.update==False and args.createtor==False:
        print("you must set -prepare or -upload or -update or -createtor")
        return False
    if os.path.isdir(args.media) and len(os.listdir(args.media))==0:
        print("Upload Folder is Empty")
        return False
    return True

"""
Return a list of files

:param args: user Commandline/Config arguments
:returns: Returns a string or list based on type of path for args.media
"""
def get_choices(args):
     if (args.batch in ["T","True","t","true",True]) and os.path.isdir(args.media):
         return sorted(os.listdir(args.media))
     else:
         return [args.media]
"""
Performs Action on single directory/File based on User input

:param args: user Commandline/Config arguments
:param path: path chosen by user
:returns: None
"""
def single_upload(args,path):
    basename=get_upload_name(path)
    print("test200",basename)
    if args.prepare:
        print("Prepare Mode\n")
        yamlpath=emp.start_yaml(basename,args)
        emp.process_yaml(path,args,yamlpath)
    if args.upload:
        print("Upload Mode\n")
        emp.pre_upload_emp(args,path)
    if args.update:
        print("Update Template Mode\n")
        yamlpath=emp.start_yaml(basename,args)
        emp.update_template(args,yamlpath)
    if args.createtor:
        print("Torrent Creator Mode\n")
        torrentpath=os.path.join(args.torrents,f"{basename}.torrent")
        emp.create_torrent(path,torrentpath,args)


"""
Prompts User to Select a specific file/Directory

:param args: user Commandline/Config arguments
:param choices: List of Possible Paths
:returns: None
"""
def batch_upload(args,choices):
    keepgoing="yes"
    while keepgoing=="Yes" or keepgoing=="yes" or keepgoing=="Y" or keepgoing=="y"  or keepgoing=="YES":
        menu_entry_index=None
        if sys.platform!="win32":
            menu = TerminalMenu(choices)
            menu_entry_index = menu.show()
        else:
            menu_entry_index = SelectionMenu.get_selection(choices)  
        menu_entry_index=int(menu_entry_index)
        if menu_entry_index>= len(choices) or menu_entry_index< 0   \
        or isinstance(menu_entry_index,int)==False:
            print("Please Enter Valid Input")
            continue
        path=choices[int(menu_entry_index)]
        path=os.path.join(args.media,path)
        basename=get_upload_name(path)
        single_upload(args,path)
        if args.prepare:
            keepgoing=input("Prepare Another Upload: ")
        if args.upload:
            keepgoing=input("Upload Another Torrent: ")
        if args.update:
            keepgoing=input("Update Another Template: ")
        if args.createtor:
            keepgoing=input("Create Another Torrent")
"""
Embedded Pre-selected Images

:param args: user Commandline/Config arguments

:returns: sets Args with Image Dict
"""


def set_template_img(args):
    images={}
    if args.images==None:
        return
    if os.path.isdir(args.images)==False:
        print("Please Provide a valid argument to args.images")
    os.chdir(args.images)
    t=subprocess.run([args.fd,'--absolute-path','-t','f'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    t=t.stdout.decode('utf-8')
    print("Adding Images from your Imagedir to YAML")
    for line in t.splitlines():
        basename=get_upload_name(line)
        
        link=network.fapping_upload(False,line)
        images[basename]=link
    return images     

"""
basename of path

:param path: path chosen by user
:returns string: basename
"""
def get_upload_name(path):
    return Path(path).parts[-1]

"""
return Main Directory Path

:param: None
:returns string: path 
"""     
def get_workdir():
    workingdir=os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(workingdir)


"""
Set Binary Path on Linux

:param args: user Commandline/Config arguments

:returns: sets args for all required binaries
"""

def create_binaries_linux(args):
    workingdir=get_workdir()
    if args.font==None:
        args.font=os.path.join(workingdir,"bin","mtn","OpenSans-Regular.ttf")
    if which('ffprobe')!=None and len(which('ffprobe'))>0:
        args.ffprobe=which('ffprobe')
    else:
        ffprobe=os.path.join(workingdir,"bin","ffmpeg-unix","ffprobe")
        args.ffprobe=ffprobe
    if which('ffmpeg')!=None and len(which('ffmpeg'))>0:
        args.ffmpeg=which('ffmpeg')
    else:
        ffmpeg=os.path.join(workingdir,"bin","ffmpeg-unix","ffmpeg")
        args.ffmpeg=ffmpeg
    if which('mtn')!=None and len(which('mtn'))>0:
        args.mtn=which('mtn')
    else:
        mtn=os.path.join(workingdir,"bin","mtn","mtn")
        args.mtn.exe=mtn
    if which('fd')!=None and len(which('fd'))>0:
        args.fd=which('fd')
    else:
        fd=os.path.join(workingdir,"bin","fd")
        args.fd=fd

    if which("dottorrent")!=None and len(which('dottorrent'))>0:
        args.dottorrent=which('dottorrent')
    else:
        dottorrent=os.path.join(workingdir,"bin","dottorrent")
        args.dottorrent=dottorrent
"""
Set Binary Path on Windows

:param args: user Commandline/Config arguments

:returns: sets args for all required binaries
"""


def create_binaries_windows(args):
    workingdir=get_workdir()
    if which('ffprobe.exe')!=None and len(which('ffprobe.exe'))>0:
        args.ffprobe=which('ffprobe.exe')
    else:
        ffprobe=os.path.join(workingdir,"bin","ffmpeg-win","ffprobe.exe")
        args.ffprobe=ffprobe
    if which('ffmpeg.exe')!=None and len(which('ffmpeg.exe'))>0:
        args.ffmpeg=which('ffmpeg.exe')
    else:
        ffmpeg=os.path.join(workingdir,"bin","ffmpeg-win","ffmpeg.exe")
        args.ffmpeg=ffmpeg
    if which('mtn.exe')!=None and len(which('mtn.exe'))>0:
        args.mtn=which('mtn.exe')
    else:
        mtn=os.path.join(workingdir,"bin","mtn","mtn.exe")
        args.mtn.exe=mtn
    if which('fd.exe')!=None and len(which('fd.exe'))>0:
        args.fd=which('fd.exe')
    else:
        fd=os.path.join(workingdir,"bin","fd.exe")
        args.fd=fd
    if which("dottorrent.exe")!=None and len(which('dottorrent'))>0:
        args.dottorrent=which('dottorrent')
    else:
        dottorrent=os.path.join(workingdir,"bin","dottorrent.exe")
        args.dottorrent=dottorrent
    
