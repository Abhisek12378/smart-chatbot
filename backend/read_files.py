import fitz
import easyocr
import io
import PyPDF2
from PIL import Image
from langchain.document_loaders.csv_loader import CSVLoader
from config_loader import AppConfig
from docx import Document
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

config=AppConfig()

class PDFReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.reader = easyocr.Reader(['en'])

    def extract_text_with_pypdf2(self):
        text = ""
        with open(self.filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text.strip()

    def extract_images(self, page):
        images = []
        img_list = page.get_images(full=True)
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            images.append(Image.open(io.BytesIO(image_bytes)))
        return images

    def images_to_text(self, images):
        full_text = ""
        for image in images:
            results = self.reader.readtext(image, detail=2)
            for (bbox, text,prob) in results:
                full_text += f"{text}\n"
        return full_text.strip()

    def read_file(self):
        text_content = self.extract_text_with_pypdf2()
        if text_content.strip():
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=50)
            chunks = text_splitter.create_documents([text_content])
            return chunks
            ##return text_content
        doc = fitz.open(self.filepath)
        full_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            images = self.extract_images(page)
            if images:
                full_text += self.images_to_text(images) + "\n"
            else:
                print(f"No text or images found on page {page_num + 1}.")
        doc.close()
        full_text=full_text.strip()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=50)
        chunks = text_splitter.create_documents([full_text])
        return chunks


class CSVReader:
    def __init__(self, filepath):
        self.filepath=filepath

    def read_file(self):
        loader = CSVLoader(file_path=self.filepath)
        data = loader.load()
        return  data

class TextFileReader:
    def __init__(self,filepath):
        self.filepath=filepath

    def read_file(self):
        loader = TextLoader(self.filepath)
        data=loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=100)
        chunks = text_splitter.create_documents([data[0].page_content])
        return chunks

class DocsReader:
    def __init__(self,filepath):
        self.filepath=filepath

    def read_file(self):
        doc = Document(self.filepath)
        full_text = ""
        for para in doc.paragraphs:
            full_text += para.text + "\n"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=50)
        chunks = text_splitter.create_documents([full_text])
        return chunks





















