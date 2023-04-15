import os
import pipes
import subprocess
import shutil

# Recursively walks the sexpr tree and outputs a metadata format understandable by pdftk

home = os.path.expanduser("~")
src = home + "/Desktop/djv2pdf/djvufile.djvu"
dest = "/Desktop/books/output.pdf"
tmp = home + "/Desktop/books/.dpsprep"


def walk_bmarks(bmarks, level):
    output = ''
    wroteTitle = False
    for j in bmarks:
        if isinstance(j, list):
            output = output + walk_bmarks(j, level + 1)
        elif isinstance(j, str):
            if not wroteTitle:
                output = output + f"BookmarkBegin\nBookmarkTitle: {j}\nBookmarkLevel: {level}\n"
                wroteTitle = True
            else:
                output = output + f"BookmarkPageNumber: {j.split('#')[1]}\n"
                wroteTitle = False
        else:
            pass
    return output


def check_lib():
    assert shutil.which('djvu2hocr'), 'dpsprep requires the djvu2hocr binary, which is part of ocradjvu'
    assert shutil.which('ddjvu') and shutil.which(
        'djvused'), 'dpsprep requires the ddjvu and djvused binaries, which are part of djvulibre'
    assert shutil.which('pdftk'), 'dpsprep requires pdftk'

    if not os.path.exists(home + "/Desktop/books/.dpsprep"):
        os.mkdir(home + "/Desktop/books/.dpsprep")


def check_file_processed():
    if os.path.isfile(tmp + '/inprocess'):
        fname = open(tmp + '/inprocess', 'r').read()
        if not fname == src:
            print(f"ERROR: Attempting to process {src} before {fname} is completed. Aborting.")
            exit(3)
        else:
            print(f"NOTE: Continuing to process {src}...")
    else:
        print("NOTE: Record the file we are about to process")
        # Record the file we are about to process
        open(tmp + '/inprocess', 'w').write(src)


def make_pdf():
    print("NOTE: Make the PDF, compressing with JPG so they are not ridiculous in size")
    if not os.path.isfile(tmp + '/dumpd'):
        # Пока не удается тут убрать старый формат работы со строками из-за 'pg%%06d.tif'
        retval = os.system("ddjvu -v -eachpage -format=tiff %s %s/pg%%06d.tif" % (src, tmp))
        if retval > 0:
            print("\nNOTE: There was a problem dumping the pages to tiff.  See above output")
            exit(retval)

        print("Flat PDF made.")
        open(tmp + '/dumpd', 'a').close()
    else:
        print("Inflated PDFs already found, using these...")


def dump_file():
    if not os.path.isfile(tmp + '/beadd'):
        cwd = os.getcwd()
        os.chdir(tmp)
        retval = os.system('pdfbeads * > ' + dest)
        if retval > 0:
            print("\nNOTE: There was a problem beading, see above output.")
            exit(retval)

        print("Beading complete.")
        open('beadd', 'a').close()
        os.chdir(cwd)
    else:
        print("Existing destination found, assuming beading already complete...")


if __name__ == "__main__":
    # # From Python docs, nice and slick command line arguments
    # parser = argparse.ArgumentParser(
    #     description='Convert DJVU format to PDF format preserving OCRd text and metadata.  Very useful for Sony Digital Paper system')
    # parser.add_argument('src', metavar='djvufile', type=str,
    #                     help='the source DJVU file')
    # parser.add_argument('dest', metavar='pdffile', type=str,
    #                     help='the destination PDF file')
    # parser.add_argument('-q, --quality', dest='quality', type=int, default=80,
    #                     help='specify JPEG lossy compression quality (50-150).  See man ddjvu for more information.')
    #
    # args = parser.parse_args()
    check_lib()
    # Reescape the filenames because we will just be sending them to commands via system
    # and we don't otherwise work directly with the DJVU and PDF files.
    # Also, stash the temp pdf in the clean spot
    # args.src = pipes.quote(args.src)
    # finaldest = pipes.quote(args.dest)
    # args.dest = home + '/.dpsprep' + pipes.quote(args.dest)

    src = pipes.quote(src)
    finaldest = pipes.quote(dest)
    dest = home + pipes.quote(dest)

    # args.dest = home + pipes.quote(args.dest)

    # Check for a file presently being processed
    check_file_processed()

    # Make the PDF, compressing with JPG so they are not ridiculous in size
    # (cwd)
    make_pdf()

    # Extract and embed the text
    # if not os.path.isfile(tmp + '/hocrd'):
    #     cnt = int(subprocess.check_output(f"djvused {src} -u -e n", shell=True))
    #     for i in range(1, cnt):
    #         retval = os.system(f"djvu2hocr -p {i} {src} | sed 's/ocrx/ocr/g' > {tmp}/pg{str(1000000 + i)[1:7]}.html")
    #         if retval > 0:
    #             print(f"\nNOTE: There was a problem extracting the OCRd text on page {i}, see above output.")
    #             exit(retval)
    #
    #     print("OCRd text extracted.")
    #     open(tmp + '/hocrd', 'a').close()
    # else:
    #     print("Using existing hOCRd output...")

    # Is sloppy and dumps to present directory
    dump_file()

    ###########################$
    #
    # At this point, the OCRd text is now properly placed within the PDF file.
    # Now, we need to add the links and table of contents!

    # Extract the bookmark data from the DJVU document
    # (scratch)
    # retval = 0
    # retval = retval | os.system(f"djvused {src} -u -e 'print-outline' > {tmp}/bmarks.out")
    # print("Bookmarks extracted.")
    #
    # # Check for zero-length outline
    # if os.stat(f"{tmp}/bmarks.out").st_size > 0:
    #
    #     # Extract the metadata from the PDF document
    #     retval = retval | os.system(f"pdftk {dest} dump_data_utf8 > {tmp}/pdfmetadata.out")
    #     print("Original PDF metadata extracted.")
    #
    #     # Parse the sexpr
    #     pdfbmarks = walk_bmarks(sexpdata.load(open(tmp + '/bmarks.out')), 0)
    #
    #     # Integrate the parsed bookmarks into the PDF metadata
    #     p = re.compile('NumberOfPages: [0-9]+')
    #     metadata = open(f"{tmp}/pdfmetadata.out", 'r').read()
    #
    #     for m in p.finditer(metadata):
    #         loc = int(m.end())
    #
    #         newoutput = metadata[:loc] + "\n" + pdfbmarks[:-1] + metadata[loc:]
    #
    #         # Update the PDF metadata
    #         open(f"{tmp}/pdfmetadata.in", 'w').write(newoutput)
    #         retval = retval | os.system(
    #             f"pdftk {dest} update_info_utf8 {tmp + '/pdfmetadata.in'} output {finaldest}")
    #
    # else:
    #     retval = retval | os.system(f"mv {dest} {finaldest}")
    #     print("No bookmarks were present!")

    # If retval is shit, don't delete temp files
    # if retval == 0:
    #     os.system(f"rm {tmp}/*")
    #     print("SUCCESS. Temporary files cleared.")
    #     exit(0)
    # else:
    #     print(
    #         "There were errors in the metadata step.  OCRd text is fine, pdf is almost ready.  See above output for cluse")
    #     exit(retval)

    os.system(f"rm {tmp}/*")
    print("SUCCESS. Temporary files cleared.")
