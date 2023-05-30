import os
import pipes
import shutil

# Recursively walks the sexpr tree and outputs a metadata format understandable by pdftk

home = os.path.expanduser("~")
src = home + "/Desktop/djv2pdf/djvufile.djvu"
dest = "/Desktop/books/output.pdf"
tmp = home + "/Desktop/books/.dpsprep"


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
    # Check libs
    check_lib()

    src = pipes.quote(src)
    finaldest = pipes.quote(dest)
    dest = home + pipes.quote(dest)


    # Check for a file presently being processed
    check_file_processed()

    # Make the PDF, compressing with JPG so they are not ridiculous in size
    # (cwd)
    make_pdf()

    # Is sloppy and dumps to present directory
    dump_file()

    os.system(f"rm {tmp}/*")
    print("SUCCESS. Temporary files cleared.")
