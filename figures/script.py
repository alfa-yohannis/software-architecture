import os
import subprocess
import threading

def process_single_pdf(pdf_path):
    foldername = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path)
    ps_filename = filename[:-4] + '.ps'
    ps_path = os.path.join(foldername, ps_filename)

    print(f"Processing: {pdf_path}")

    # Convert PDF to PS
    try:
        subprocess.run(['pdftops', pdf_path], check=True)
        print(f"Converted to PS: {ps_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting to PS: {e}")
        return

    # Convert PS back to PDF
    try:
        subprocess.run(['epstopdf', ps_path], check=True)
        print(f"Converted back to PDF: {ps_filename[:-3]}.pdf")
    except subprocess.CalledProcessError as e:
        print(f"Error converting back to PDF: {e}")
        return

    # Remove PS file
    try:
        os.remove(ps_path)
        print(f"Removed PS file: {ps_path}")
    except OSError as e:
        print(f"Error deleting PS file: {e}")

def process_pdfs(root_folder):
    threads = []
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(foldername, filename)
                # Create a thread for each PDF file
                t = threading.Thread(target=process_single_pdf, args=(pdf_path,))
                t.start()
                threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("All PDF files processed.")

if __name__ == '__main__':
    target_folder = input("Enter the path to the folder: ")
    process_pdfs(target_folder)
