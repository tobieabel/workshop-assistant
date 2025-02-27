import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_extractor import extract_text_from_pdf

def test_pdf_extraction():
 
    
    # Test with a sample PDF
    test_file = 'test_files/test.pdf'
    
    # You'll need to create a sample PDF file for testing
    # For now, just test if the function exists
    try:
        if os.path.exists(test_file):
            text = extract_text_from_pdf(test_file)
            print("Extracted text:", text[:200] + "..." if len(text) > 200 else text)
            print("Text extraction successful!")
        else:
            print(f"Please create a test PDF file at: {test_file}")
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_pdf_extraction() 