import  paperinquierer

pdf_dir = "path/to/pdf/files"
question = "A/question/to/ask"

a = paperinquierer.PaperInquirer(pdf_dir)
print(a.inquire(question))