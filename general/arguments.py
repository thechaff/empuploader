import os
from jsonargparse import ArgumentParser, ActionConfigFile
import settings as settings
"""
sets up Argument Parser with required settings
:param: None
:return: parsed args
"""
def getargs():
    parser = ArgumentParser(prog="empuploader")
    parser.add_argument('-c','--config', action=ActionConfigFile,help="override config file")  
    parser.add_argument('-k','--cookie',help="cookie File for preview and upload mode",required=False)
    parser.add_argument("-t","--template",help="Template file for creating upload file",default=os.path.join(settings.workingdir,"data/default_template.txt"))

    prepare = ArgumentParser(description="Prepare a upload by creating a YAML File\nFilled with configurations")
    prepare.add_argument("-b","--batch",help="Seperate a folder into seperate entries for upload", action='store_true')
    prepare.add_argument('-m','--media',help="Directory to retrive media files",required=True)
    prepare.add_argument('-t','--torrent',help="Directory to store torrent files",required=True)
    prepare.add_argument('-p','--picdir',help="Path to store output mediafiles\nStored in tmpfile if not set",required=False)
    prepare.add_argument('-tr','--tracker',help="announce url",required=True)
    prepare.add_argument('-c','--cover',help="set a preset image to use for torrent cover",required=False)
    prepare.add_argument('-i','--images',help="Folder with static images for upload",required=False)
    prepare.add_argument('-e','--exclude',help="file patterns for dottorrent to exclude\nCan be passed multiple times",required=False,nargs='*',default=[])

    # upload= ArgumentParser()
    edit= ArgumentParser()
    preview= ArgumentParser()
    upload= ArgumentParser()
    subcommands = parser.add_subcommands()
    subcommands.add_subcommand('prepare',prepare, help="prepare mediafile for upload")
    subcommands.add_subcommand('preview',preview,help="upload to emp")
    subcommands.add_subcommand('edit',edit,help="edit a upload configuration yml")
    subcommands.add_subcommand('upload',upload,help="upload torrent")


    parser.add_argument("-o","--output",help="Path to Dir or a full filepath terminated with .yml or .yaml",required=True)
    args=parser.parse_args()
    if (args.subcommand=="upload" or args.subcommand=="preview") and args.cookie==None:
        print("Cookie arg must be set")
        quit()
    return args