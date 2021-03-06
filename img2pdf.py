#!/usr/bin/env python3
from os import listdir, access, W_OK, F_OK, R_OK, path, getcwd
from sys import argv, exit
from getopt import getopt, GetoptError
from PIL import Image
from fpdf import FPDF
from magic import Magic

if __name__=="__main__":
    try:

        # Define color prints
        def red_text(text): return f"\033[91m{text}\033[00m"
        def green_text(text): return f"\033[92m{text}\033[00m"
        def yellow_text(text): return f"\033[93m{text}\033[00m"
        def blue_text(text): return f"\033[96m{text}\033[00m"

        # Get command line arguments
        try:
            opts,args=getopt(argv[1:],"hd:qrfDiesp:",["help","dir=","quiet","reverse","force","decline","interactive","except","selective","page-size="])
        except GetoptError as err:
            print(err)
            exit(2)
        opts=dict((opt[0],opt[1]) for opt in opts)
        optk=opts.keys()
        
        # Print help dialog and exit
        if "-h" in optk or "--help" in optk:
            print("""This program merges image files in a directory and creates a PDF file. Every image get put to a page that exact same size as itself.
        
        Usage:
            img2pdf [OPTIONS] [OUTPUT FILE]
        
        Parameters:
            -h, --help             : Print this help document and exit.
            -d, --dir [DIRECTORY]  : Set directory to work on. Default is working directory.
            -q, --quiet            : Do not print process details.
            -r, --reverse          : Reverse image order.
            -f, --force            : Overwrite to exiting PDF file.
            -i, --interactive      : Promt before overwrite.
            -D, --decline          : Do not let overwrite. Ignores --force and --interactive parameter. 
                                     This option does not return any error if file already exists.
            -e, --except           : Do not include images that have no read permission.
            -s, --selective        : Let selecting which image will be included.
            -p, --page-size [SIZE] : Fixed page size, strech photos to page.
                                     Options are: A4, A3, A5, Letter, Legal, WITDHxHEIGHT (in pt).
        
        Exit Codes:
              0 : Program done it's job successfully.
              1 : An error occurred.
              2 : Parameter fault. Please check your command.
              3 : No valid image file in directory.
              4 : User declined overwrite.
              5 : File exist and overwrite not allowed. 
            126 : File permission denied. Check file permissions.
            130 : Process terminated by user.""")
            exit(0)
        
        # Check for arguments
        if len(args)==0:
            print(red_text("img2pdf: Error: Please specify output file."))
            exit(2)
        
        if len(args)==1:
        
            # Required objects and directory
            pdf=FPDF(unit="pt")
            mime=Magic(mime=True)
            directory=opts["-d"] if "-d" in optk else (opts["--dir"] if "--dir" in optk else getcwd())
            directory=directory+("" if directory.endswith("/") else "/")
                    
            if len(args)==1:
        
                # Get output file name.
                file_name=directory+args[0]+("" if args[0].endswith(".pdf") else ".pdf")
                
                # Check for existing files
                if access(file_name,F_OK):
                    
                    # Get Modification time to use in process validation
                    modification_time=path.getmtime(file_name)
        
                    # Check for file permission
                    if not access(file_name,W_OK):
                        print(red_text(f"img2pdf: Permission Denied: The file '{file_name}' is not writable. Check file permissions."))
                        exit(126)
                    
                    # Check if forced
                    if "-f" not in optk and "--force" not in optk:
        
                        # Check if declined
                        if "-D" in optk or "--decline" in optk:
                            print(blue_text("img2pdf: Quit: Forced to decline overwrite."))
                            exit(0)
        
                        # Check if interactive
                        elif "-i" in optk or "--interactive" in optk:
                            if input(yellow_text("img2pdf: Prompt: File is already exists. Do you want to overwrite? [y/N]: ")).lower() not in ("y","yes"):
                                print(red_text("img2pdf: Quit: User declined overwrite."))
                                exit(4)
                        else:
                            print(red_text("img2pdf: Quit: File already exists. To overwrite add -f or --force parameter."))
                            exit(5)
        
                # If file not exists create a fake modification time
                else:
                    modification_time=0
             
                # Get image Files
                all_files=listdir(directory)
                all_files.sort()
                images=[]
                
                # Check for selective
                selective=True if "-s" in optk or "--selective" in optk else False
            
                # Get image files
                for file in all_files:
    
                    # Check for read permission
                    if access(directory+file,R_OK):
                    
                        # Be sure element is not directory
                        if path.isfile(directory+file):
    
                            # Check if file is image by it's mimetype
                            if "image/" in mime.from_file(directory+file):
    
                                # Select items is selective
                                if selective:
                                    if input(blue_text(f"Include \"{file}\"? [Y/n]: ")).lower() in ("y","yes",""):
                                        images.append(directory+file)
                                        print(green_text(f"  {file} will be add."))
                                    else:
                                        print(red_text(f"  {file} will be pass."))
                                else:
                                    images.append(directory+file)
                        else:
                            continue
                    elif "-e" in optk or "--except" in optk:
                        continue
                    else:
                        print(red_text(f"img2pdf: Permission Denied: The file '{file}' is not readable. Check file permissions or pass -e parameter to not include it."))
                        exit(126)
            
                # Count images
                image_count=len(images)
                image_count_digits=len(str(image_count))
            
                # There is no image
                if image_count==0:
                    print(red_text("img2pdf: Error: There is no valid image file to work with."))
                    exit(3)
            
                # Check for reverse
                if "-r" in optk or "--reverse" in optk:
                    images.reverse()
                    print(blue_text("Image order reversed."))
    
                # Check for page size
                page_size=""
                if "-p" in optk:
                    page_size=opts["-p"].lower()
                if "--page-size" in optk:
                    page_size=opts["--page-size"].lower()
        
                # Check for standard page sizes
                if page_size=="a3":
                    print(blue_text("Page size set to A3."))
                    size,width,height="a3",842,1191
                elif page_size=="a4":
                    print(blue_text("Page size set to A4."))
                    size,width,height="a4",595,842
                elif page_size=="a5":
                    print(blue_text("Page size set to A5."))
                    size,width,height="a5",420,595
                elif page_size=="letter":
                    print(blue_text("Page size set to Letter."))
                    size,width,height="letter",612,792
                elif page_size=="legal":
                    print(blue_text("Page size set to Legal."))
                    size,width,height="legal",612,1008
                    
                # Check manual dimensions
                elif "x" in page_size and not page_size.startswith("x") and not page_size.endswith("x"):
                    dimensions=page_size.split("x") 
                    if len(dimensions)==2:
                        
                        # Get width
                        try:
                            width=int(dimensions[0])
                        except:
                            print(red_text(f"img2pdf: Invalid Argument: Width parameter which is {dimensions[0]} must be an integer."))
                            exit(2)

                        # Get height
                        try:
                            height=int(dimensions[1])
                        except:
                            print(red_text(f"img2pdf: Invalid Argument: Height parameter which is {dimensions[1]} must be an integer."))
                            exit(2)
                    else:
                        print(red_text("img2pdg: Invalid Argument: --page-size parameter must be integers connected with \"x\"."))
                        exit(2)
                    page_size="user_defined"
                    print(blue_text(f"Page size set to {width}x{height}"))
        
                # Check for unvalid page sizes.
                elif page_size!="":
                    print(red_text(f"img2pdf: Invalid Argument: --page-size parameter which is \"{page_size}\" can only take this parameters: ")+ blue_text("A3, A4, A5, Letter, Legal, WIDTHxHEIGHT (in pt)."))
                    exit(2)
                else:
                    print(blue_text("Every image will be placed a page that fits their size."))
        
                # Finally start job
                for number,image in enumerate(images):               
                    
                    # Check if user defined fixed size
                    if page_size=="user_defined":
                        pdf.add_page(format=(width,height))
        
                    # Check if standard fixed size
                    elif page_size:
                        pdf.add_page(format=size)
        
                    # Else use dimensions by image
                    elif not page_size:
                        width,height=Image.open(image).size
                        pdf.add_page(format=(width,height))
                    
                    # Add image to recently created page
                    pdf.image(image,0,0,width,height)
        
                    # Check if quiet
                    if "-q" not in optk and "--quiet" not in optk:
                        print(f"{str(number+1).rjust(image_count_digits)}/{image_count}: Adding image {image}")
        
                # Write PDF
                pdf.output(file_name)
        
                # Check if it really done
                if access(file_name,F_OK):
                    if path.getmtime(file_name)!=modification_time:
                        print(green_text("img2pdf: Success: PDF file created."))
                        exit(0)
                    else:
                        print(red_text("img2pdf: Error: And error occured. Could not modify the existed file."))
                        exit(1)
                else: 
                    print(red_text("img2pdf: Error: An error occurred. Could not create the PDF."))
                    exit(1)
        
        # Wrong argument count
        else:
            print(red_text("img2pdf: Error: Please give only one parameter to specify output file."))
            exit(2)
        
        # Unexpected Errors
        print(red_text("img2pdf: Error: An unexpected error occurred. Please contact with developer if you can recognize the problem."))
        exit(1)

    # Handle Control+C interruption
    except KeyboardInterrupt:
        print('\nimg2pdf: Quit: Process terminated by user.')
        exit(130)
