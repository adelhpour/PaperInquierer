import  paperinquierer

pdf_dir = "path/to/pdf/files"
abstract_dir = "path/to/abstract/files"
storage_dir = "path/to/storage"
question = "A/question/to/ask"

a = paperinquierer.PaperInquirer(pdf_dir, abstract_dir, storage_dir, storage_dir)
print(a.inquire(question))