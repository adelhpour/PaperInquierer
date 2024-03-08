import paperinquirer

pdf_dir = "path/to/pdf/files"
abstract_dir = "path/to/abstract/files"
storage_dir = "path/to/storage"
question = "A/question/to/ask"

inquirer = paperinquirer.PaperInquirer(pdf_dir, abstract_dir, storage_dir)
print(inquirer.inquire(question))
